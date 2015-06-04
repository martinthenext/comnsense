import logging
import uuid

from comnsense_agent.message import Message
from comnsense_agent.data import Event, Action, Request, Signal, Response
from comnsense_agent.context import Context

logger = logging.getLogger(__name__)


class State:
    pass


class WaitingWorkbookID:
    """
    Waiting for workbook id from excel
    """
    def next(self, context, msg):
        if msg.is_event():
            event = Event.deserialize(msg.payload)
            context.workbook = event.workbook
        elif msg.is_signal():
            signal = Signal.deserialize(msg.payload)
            context.workbook = signal.data
        if context.workbook:
            if not context.is_ready():
                # get context from server
                request = Message.request(Request.getcontext(context.workbook))
                return request, State.WaitingContext
            else:
                return None, State.WaitingEvent
        return None, self


class WaitingContext:
    """
    Waiting context from server
    """
    def next(self, context, msg):
        if msg.is_response():
            response = Response.deserialize(msg.payload)
            context.loads(response.data)
        if context.is_ready():
            return None, State.Ready
        return None, self


class Ready:
    """
    Context is ready
    """
    def next(self, context, msg):
        if msg.is_event():
            event = Event.deserialize(msg.payload)
            # proceed event
            return None, self
        return None, self


State.WaitingWorkbookID = WaitingWorkbookID()
State.WaitingContext = WaitingContext()
State.Ready = Ready()


class Runtime:
    def __init__(self):
        self.currentState = State.WaitingWorkbookID
        self.context = Context()

    def run(self, message):
        with self.context as context:
            answer, self.currentState = \
                self.currentState.next(context, message)
            return answer
