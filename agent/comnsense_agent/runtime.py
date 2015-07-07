import logging
import uuid

from comnsense_agent.message import Message
from comnsense_agent.data import Event, Action, Request, Signal, Response
from comnsense_agent.data import Cell, Border
from comnsense_agent.context import Context

from comnsense_agent.automaton.initialization import WaitingWorkbookID
from comnsense_agent.automaton.initialization import WaitingContext
from comnsense_agent.automaton.ready import Ready

from comnsense_agent.automaton import State

logger = logging.getLogger(__name__)


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
