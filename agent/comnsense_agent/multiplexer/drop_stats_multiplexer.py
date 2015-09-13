import logging
import itertools

from comnsense_agent.data import Action, Event
from .single_change_all_requests import SingleChangeAllRequests
from .multiplexer import Multiplexer

logger = logging.getLogger(__name__)


class DropStatsMultiplexer(Multiplexer):
    def __init__(self, context):
        self._multiplexer = SingleChangeAllRequests()
        self._context = context

    def merge(self, event, answers):
        answer = self._multiplexer.merge(event, answers)
        self._invalidate(event, answer)
        return answer

    def _invalidate(self, event, answer):
        if event.type in (Event.Type.WorkbookOpen,
                          Event.Type.WorkbookBeforeClose):
            return answer

        event_values = {
            (x.key, x.value) for x in
            itertools.chain.from_iterable(event.cells)
        }

        logger.debug("event (key,value) pairs: %s", repr(event_values))

        changes = filter(lambda x: x.type == Action.Type.ChangeCell, answer)
        cells = itertools.chain.from_iterable(
            itertools.chain.from_iterable(
                itertools.imap(lambda x: x.cells, changes)))

        # find all cells that change value, not only format
        cells = filter(lambda x: (x.key, x.value) not in event_values, cells)
        logger.debug("value changes: %s", repr(cells))

        if cells:
            self._context.lookup(changes[0].sheet).invalidate([cells])
