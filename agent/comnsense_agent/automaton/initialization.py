import logging

from comnsense_agent.message import Message
from comnsense_agent.data import Event, Action, Request, Signal, Response

from comnsense_agent.automaton import State


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
                return None, State.Ready
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
