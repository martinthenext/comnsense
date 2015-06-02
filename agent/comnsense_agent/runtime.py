import logging
import uuid

import comnsense_agent.message as M
from comnsense_agent.data import Event, Action, Request, Signal
from comnsense_agent.model import Model

logger = logging.getLogger(__name__)


class State:
    pass


class WaitingWorkbookID:
    def next(self, model, msg):
        if msg.is_event():
            event = Event.deserialize(msg.payload)
            model.workbook = event.workbook
        elif msg.is_signal():

        if model.workbook:
            excel_answer = M.Message(
                M.KIND_ACTION, Action.setid(model.workbook))
            server_request = M.Message(
                M.KIND_REQUEST, Request.getmodel(model.workbook))
            return (excel_answer, server_request), State.WaitingModel
        else:
            return None, self


class WaitingModel:
    def next(self, model, msg):
        if msg.is_response():
            # set model
            return None, State.WaitingEvent
        else:
            return None, self


class WaitingEvent:
    def next(self, model, msg):
        if msg.is_event():
            event = Event.deserialize(msg.payload)
            # proceed event
            return None, self
        else:
            return None, self

State.WaitingWorkbookID = WaitingWorkbookID()
State.WaitingModel = WaitingModel()
State.WaitingEvent = WaitingEvent()


class Runtime:
    def __init__(self):
        #  self.currentState = State.WaitingWorkbookID
        self.currentState = State.WaitingEvent
        self.model = Model()

    def run(self, message):
        answer, self.currentState = self.currentState.next(self.model, message)
        return answer
