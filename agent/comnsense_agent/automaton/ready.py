import logging

from comnsense_agent.data import Event
from comnsense_agent.message import Message

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
            answer = None
            for handler in context.handlers(event.sheet):
                logger.debug("call %s handler", handler.__class__.__name__)
                actions = handler.handle(event, context)
                if actions:
                    # all handlers should retrieve event
                    # but just first action will be send
                    if answer is None:
                        answer = tuple(map(Message.action, actions))
            return answer, self
        else:
            logger.warn("unexpected event: %s", str(event))
            return None, self
