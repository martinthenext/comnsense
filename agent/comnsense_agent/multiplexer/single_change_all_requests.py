import logging
import itertools

from comnsense_agent.data import Action
from .multiplexer import Multiplexer

logger = logging.getLogger(__name__)


class SingleChangeAllRequests(Multiplexer):
    def merge(self, event, answers):
        if not answers:
            return []

        requests = []
        changes = []
        for action in itertools.chain.from_iterable(filter(bool, answers)):
            if not action:
                continue
            if action.type == Action.Type.RangeRequest:
                requests.append(action)
            else:
                changes.append(action)

        return self._reduce_changes(changes) + requests

    def _reduce_changes(self, changes):
        if not changes:
            return []

        change = Action(
            Action.Type.ChangeCell, changes[0].workbook,
            changes[0].sheet, [[]])
        keys = set()
        cells = itertools.chain.from_iterable(
            itertools.imap(lambda x: x.cells, changes))
        for cell in itertools.chain.from_iterable(cells):
            if cell.key not in keys:
                change.cells[0].append(cell)
                keys.add(cell.key)
        return [change]
