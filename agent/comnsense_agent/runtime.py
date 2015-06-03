import logging
import uuid

from comnsense_agent.message import Message
from comnsense_agent.data import Event, Action, Request, Signal, Response
from comnsense_agent.model import Model

logger = logging.getLogger(__name__)


class State:
    pass


class WaitingWorkbookID:
    """
    Waiting for workbook id from excel
    """
    def next(self, model, msg):
        if msg.is_event():
            event = Event.deserialize(msg.payload)
            model.workbook = event.workbook
        elif msg.is_signal():
            signal = Signal.deserialize(msg.payload)
            model.workbook = signal.data
        if model.workbook:
            if not model.is_ready():
                # get model from server
                request = Message.request(Request.getmodel(model.workbook))
                return request, State.WaitingModel
            else:
                return None, State.WaitingEvent
        return None, self


class WaitingModel:
    """
    Waiting model from server
    """
    def next(self, model, msg):
        if msg.is_response():
            response = Response.deserialize(msg.payload)
            model.loads(response.data)
        if model.is_ready():
            return None, State.Ready
        return None, self


class Ready:
    """
    Model is ready
    """
    def next(self, model, msg):
        if msg.is_event():
            event = Event.deserialize(msg.payload)
            # proceed event
            return None, self
        return None, self


State.WaitingWorkbookID = WaitingWorkbookID()
State.WaitingModel = WaitingModel()
State.Ready = Ready()


class Runtime:
    def __init__(self):
        self.currentState = State.WaitingWorkbookID
        self.model = Model()

    def run(self, message):
        with self.model as model:
            answer, self.currentState = self.currentState.next(model, message)
            return answer
