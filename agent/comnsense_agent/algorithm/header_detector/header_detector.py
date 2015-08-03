import logging
import string
import enum

from ..event_handler import EventHandler, publicmethod
from comnsense_agent.data import Event, Action

logger = logging.getLogger(__name__)


class HeaderDetector(EventHandler):
    class State(enum.Enum):
        begin = "begin"
        inprogress = "in progress"
        found = "found"

    RANGE_STEP = 5

    def __init__(self):
        self._state = HeaderDetector.State.begin
        self._header = []

    def handle(self, event, context):
        if self._state == HeaderDetector.State.begin:
            action = self.handle_begin(event)
        elif self._state == HeaderDetector.State.inprogress:
            action = self.handle_inprogress(event)
        elif self._state == HeaderDetector.State.found:
            action = self.handle_found(event)
        else:
            raise AssertionError("impossible state")

        if action:
            return [action]
        else:
            return []

    @publicmethod
    def get_header(self):
        if self._state == HeaderDetector.State.found:
            return self._header

    @publicmethod
    def get_header_columns(self):
        if self._state == HeaderDetector.State.found:
            return {x.column for x in self._header}

    @publicmethod
    def get_header_rows(self):
        if self._state == HeaderDetector.State.found:
            return {x.row for x in self._header}

    def handle_begin(self, event):
        action = Action.request_from_event(event, self.get_next_range())
        self._state = HeaderDetector.State.inprogress
        return action

    def handle_inprogress(self, event):
        if event.type != Event.Type.RangeResponse:
            return

        header = event.rows.get("1")  # get only first line
        if not header:
            return

        empty = self.get_first_empty_cell_index(header)
        if empty < 0:
            self._header += header
            return Action.request_from_event(event, self.get_next_range())
        elif empty == 0:
            logger.debug("header found: %s", repr(self._header))
            self._state = HeaderDetector.State.found
            return
        else:
            self._header += header[:empty]
            logger.debug("header found: %s", repr(self._header))
            self._state = HeaderDetector.State.found
            return

    def handle_found(self, event):
        header = event.rows.get("1")
        if not header:
            return

        for new in header:
            for cell in self._header:
                if new.key == cell.key:
                    cell.value = new.value
            if new.column == self.get_next_column(self._header[-1].column):
                self._header.append(new)

    def get_next_range(self, shift=None):
        if shift is None:
            shift = self.RANGE_STEP
        if self._state == HeaderDetector.State.begin:
            return "$A$1:$E$1"
        else:
            last = self.get_index_from_column(self._header[-1].column)
            start = self.get_column_from_index(last + 1)
            end = self.get_column_from_index(last + shift)
            return "$%s$1:$%s$1" % (start, end)

    def get_first_empty_cell_index(self, header):
        mask = [True if cell.value else False for cell in header]
        try:
            return mask.index(False)
        except ValueError:
            return -1

    def get_index_from_column(self, column):
        s = string.ascii_uppercase
        l = len(s)
        return sum([(s.index(x) + 1) * (l ** i)
                    for i, x in enumerate(reversed(column))]) - 1

    def get_column_from_index(self, index):
        s = string.ascii_uppercase
        l = len(s)
        if index < l:
            return s[index]
        else:
            result = ""
            result += s[index / l - 1]
            result += s[index - (index / l) * l]
            return result

    def get_next_column(self, column, shift=1):
        index = self.get_index_from_column(column)
        return self.get_column_from_index(index + shift)
