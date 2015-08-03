import logging

from comnsense_agent.automaton import State
from comnsense_agent.data import Request, Event, Signal
from comnsense_agent.message import Message

logger = logging.getLogger(__name__)


class WaitingWorkbookID:
    """
    Waiting for workbook id from excel
    """
    def next(self, context, msg):
        if msg.is_event():
            event = Event.deserialize(msg.payload)
            if event.type == Event.Type.WorkbookBeforeClose:
                return None, None
            context.workbook = event.workbook
        else:
            return None, self

        if not context.workbook:
            return None, self
        if context.is_ready():
            return None, State.Ready

        # get context from server
        request = Message.request(
            Request.getcontext(context.workbook))
        return request, State.WaitingContext
