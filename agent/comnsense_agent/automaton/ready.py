import logging
from collections import OrderedDict

from comnsense_agent.algorithm.error_detector import ErrorDetector
from comnsense_agent.algorithm.header_detector import HeaderDetector
from comnsense_agent.algorithm.string_formatter import StringFormatter

from comnsense_agent.automaton import State
from comnsense_agent.data import Event
from comnsense_agent.message import Message

logger = logging.getLogger(__name__)


class Ready:
    """
    Context is ready
    """

    def add_new_sheet(self, context, sheet):
        context.sheets_event_handlers[sheet] = OrderedDict([
            (HeaderDetector.__name__, HeaderDetector()),
            (StringFormatter.__name__, StringFormatter()),
            (OnlineQuery.__name__, OnlineQuery()),
        ])

    def next(self, context, msg):
        if msg.is_event():
            event = Event.deserialize(msg.payload)
            if event.type == Event.Type.WorkbookBeforeClose:
                # TODO do something here before shutdown worker
                return None, None  # special value to close runtime

            if event.sheet not in context.sheets_event_handlers:
                self.add_new_sheet(context, event.sheet)
                # TODO remove repr here
                logger.debug("new sheet: %s", event.sheet)

            handlers = context.sheets_event_handlers[event.sheet]

            if event.type in (Event.Type.SheetChange,
                              Event.Type.RangeResponse):
                answer = None
                for name, handler in handlers.iteritems():
                    logger.debug("call %s handler", name)
                    actions = handler.handle(event, context)
                    if actions:
                        if answer is None:
                            answer = tuple(map(Message.action, actions))
                        else:
                            logger.warn("skip this actions from %s", name)
                return answer, self
            else:
                logger.warn("unexpected event: %s", str(event))
                return None, self

        return None, self
