import logging
import enum

from comnsense_agent.context import Context

from comnsense_agent.automaton.waiting_workbook import WaitingWorkbookID
from comnsense_agent.automaton.waiting_context import WaitingContext
from comnsense_agent.automaton.ready import Ready

from comnsense_agent.automaton import State

logger = logging.getLogger(__name__)


State.WaitingWorkbookID = WaitingWorkbookID()
State.WaitingContext = WaitingContext()
State.Ready = Ready()


class Runtime(object):

    @enum.unique
    class SpecialAnswer(enum.Enum):
        noanswer = "no answer"
        finished = "finished"

    def __init__(self):
        self.currentState = State.WaitingWorkbookID
        self.context = Context()

    def prepare_answer(self, answer):
        if self.currentState is None:
            return Runtime.SpecialAnswer.finished
        if answer is None:
            return Runtime.SpecialAnswer.noanswer
        if isinstance(answer, tuple):
            return list(answer)
        else:
            return [answer]

    def run(self, message):
        logger.debug("state before: %s", self.currentState.__class__.__name__)
        with self.context as context:
            answer, self.currentState = \
                self.currentState.next(context, message)
            logger.debug(
                "state after: %s", self.currentState.__class__.__name__)
            return self.prepare_answer(answer)
