import logging

from comnsense_agent.data import Event
from comnsense_agent.message import Message
from comnsense_agent.multiplexer.single_change_all_requests \
    import SingleChangeAllRequests

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

            answers = []
            for handler in context.handlers(event.sheet):
                logger.debug("call %s handler", handler.__class__.__name__)
                try:
                    answers.append(handler.handle(event, context))
                except Exception, e:
                    logger.exception(e)

            answer = SingleChangeAllRequests().merge(event, answers)
            return list(map(Message.action, answer)), self
        else:
            logger.warn("unexpected event: %s", str(event))
            return None, self
