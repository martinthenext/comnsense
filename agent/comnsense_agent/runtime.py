import logging

from comnsense_agent.context import Context

from comnsense_agent.automaton.initialization import WaitingWorkbookID
from comnsense_agent.automaton.initialization import WaitingContext
from comnsense_agent.automaton.ready import Ready
from comnsense_agent.automaton.header_request import WaitingHeader

from comnsense_agent.automaton import State

logger = logging.getLogger(__name__)


State.WaitingWorkbookID = WaitingWorkbookID()
State.WaitingContext = WaitingContext()
State.Ready = Ready()
State.WaitingHeader = WaitingHeader()


class Runtime(object):
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
