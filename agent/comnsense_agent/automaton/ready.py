import logging

from comnsense_agent.data import Event
from comnsense_agent.message import Message
from comnsense_agent.multiplexer.first_answer import FirstAnswer

logger = logging.getLogger(__name__)


class Ready:
    """
    Context is ready
    """

    def next(self, context, msg):
        if not msg.is_event():
            return None, self

        event = Event.deserialize(msg.payload)
        if event.type == Event.Type.WorkbookBeforeClose:
            # TODO do something here before shutdown worker
            return None, None  # special value to close runtime

        if event.type in (Event.Type.SheetChange,
                          Event.Type.RangeResponse):

            actions = []
            for handler in context.handlers(event.sheet):
                logger.debug("call %s handler", handler.__class__.__name__)
                actions.append(handler.handle(event, context))

            answer = FirstAnswer().merge(event, actions)
            return tuple(map(Message.action, answer)), self
        else:
            logger.warn("unexpected event: %s", str(event))
            return None, self
