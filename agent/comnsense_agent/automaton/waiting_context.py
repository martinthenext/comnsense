import logging

from comnsense_agent.automaton import State
from comnsense_agent.data import Response, Event

logger = logging.getLogger(__name__)


class WaitingContext:
    """
    Waiting context from server
    """
    def next(self, context, msg):
        if msg.is_event():
            event = Event.deserialize(msg.payload)
            if event.type == Event.Type.WorkbookBeforeClose:
                return None, None

        if msg.is_response():
            response = Response.deserialize(msg.payload)
            context.loads(response.data)

        if context.is_ready():
            return None, State.Ready

        return None, self
