import logging
import uuid

import comnsense_agent.message as M
from comnsense_agent.data import Event, Action, Request

logger = logging.getLogger(__name__)


class State:
    def next(self, model, msg):
        raise NotImplementedError()


class WaitingWorkbookID:
    def next(self, model, msg):
        if msg.is_response():
            # deserialize response here
            # get id
            # and send it to excel
            model.workbook = uuid.uuid1()
        elif msg.is_event():
            event = Event.deserialize(msg.payload)
            model.workbook = event.workbook
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


class Model:
    def __init__(self):
        self.workbook = None


class Algorithm:
    def __init__(self):
        #  self.currentState = State.WaitingWorkbookID
        self.currentState = State.WaitingEvent
        self.model = Model()

    def run(self, message):
        answer, self.currentState = self.currentState.next(self.model, message)
        return answer
