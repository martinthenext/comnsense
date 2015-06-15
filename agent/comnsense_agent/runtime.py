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
            # test: write something in "A1" for jokes
            json_to_send = """ {
                "type" : 0,
                "workbook" : "f1f2d913-8de3-49b6-8993-f6b026686cda",
                "sheet": "\xd0\xb2\xd0\xb0\xd1\x81\xd0\xb8\xd0\xbb\xd0\xb8\xd0\xb9",
                "cells":[[{"key":"$A$1","value":"33","color":0,"fontstyle":0}]]
            }
            """
            action = Action(Action.Type.ChangeCell, json_to_send)
            logger.debug("Action JSON is sent")
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
        logger.debug("state before: %s", self.currentState.__class__.__name__)
        with self.context as context:
            answer, self.currentState = \
                self.currentState.next(context, message)
            logger.debug(
                "state after: %s", self.currentState.__class__.__name__)
            return answer
