import copy
import enum
import logging
from collections import namedtuple

from comnsense_agent.data import Event, Action

from .column_analyzer import ColumnAnalyzer


logger = logging.getLogger(__name__)


class ColumnErrorDetector(object):
    BINOM_THRESHOLD = 0.1
    MIN_POINTS_READY = int(1.0 / BINOM_THRESHOLD)

    Stats = namedtuple("Stats", ("points", "stats"))

    Interval = namedtuple("Interval", ("begin", "end"))

    class State(enum.Enum):
        begin = "begin"
        waiting_response = "waiting response"
        ready = "ready"

    def __init__(self, column):
        self.column = column
        self.state = self.State.begin
        self.stats = self.Stats(0, [])
        self.interval = self.Interval(0, 0)
        self.incorrect_format = {"color": 3}
        self.correct_format = {"color": 0}

    def handle(self, event, context):
        logger.debug("column %s: state: %s",
                     self.column, self.state.value)
        logger.debug("column %s: stats: %s",
                     self.column, repr(self.stats))
        logger.debug("column %s: interval: %s",
                     self.column, repr(self.interval))

        if self.state == self.State.begin:
            return self.handle_begin(event, context)
        elif self.state == self.State.waiting_response:
            return self.handle_waiting_response(event, context)
        elif self.state == self.State.ready:
            return self.handle_ready(event, context)
        else:
            raise AssertionError("impossible state")

    def handle_begin(self, event, context):
        cells = event.columns.get(self.column, [])
        for cell in cells:
            if cell.value:
                self.add_value_to_stats(cell.value)
            self.update_interval(int(cell.row))
        self.state = self.State.waiting_response
        return [self.make_action_request(event, context)]

    def handle_waiting_response(self, event, context):
        cells = event.columns.get(self.column, [])
        request_next_range = False
        non_empty_range_end = len(cells)
        answer = []

        try:
            non_empty_range_end = \
                len(cells) - \
                [x.value for x in reversed(cells)].index("")
        except ValueError:
            request_next_range = True

        if event.type != Event.Type.RangeResponse:
            request_next_range = True

        for cell in cells[:non_empty_range_end]:
            if cell.value:
                self.add_value_to_stats(cell.value)
            self.update_interval(int(cell.row))

        if request_next_range:
            answer = [self.make_action_request(event, context)]
        else:
            self.state = self.State.ready

        if self.stats.points >= self.MIN_POINTS_READY:
            self.state = self.State.ready

        return answer

    def handle_ready(self, event, context):
        if event.type == Event.Type.SheetChange:
            return self.handle_ready_change(event, context)
        elif event.type == Event.Type.RangeResponse:
            return self.handle_ready_response(event, context)
        else:
            raise AssertionError(
                "unexpected event type: %s" % event.type.value)

    def handle_ready_change(self, event, context):
        answer_cells = []

        cells = event.columns.get(self.column, [])
        prev_cells = event.prev_columns.get(self.column, [])
        if not prev_cells:
            prev_cells = [None] * len(cells)

        for cell, prev_cell in zip(cells, prev_cells):
            prev_value = prev_cell.value if prev_cell else ""

            if cell.value and prev_value and \
                    self.interval.begin <= int(cell.row) and \
                    int(cell.row) <= self.interval.end and \
                    self.match_format(prev_cell, **self.incorrect_format):

                self.record_corrected(cell.value, prev_value)
                answer_cells.append(
                    self.apply_format(cell, **self.correct_format))

            # let's check just new values
            elif cell.value and not prev_value:
                self.add_value_to_stats(cell.value)
                if self.check(cell.value) == 0:
                    answer_cells.append(
                        self.apply_format(cell, **self.incorrect_format))

            self.update_interval(int(cell.row))

        if answer_cells:
            return [self.make_action_change(event, answer_cells)]
        else:
            return []

    def handle_ready_response(self, event, context):
        cells = event.columns.get(self.column, [])
        for cell in cells:
            if cell.value and self.interval.end < int(cell.row):
                self.add_value_to_stats(cell.value)
            self.update_interval(int(cell.row))
        return []

    def update_interval(self, row):
        if self.interval.begin <= row <= self.interval.end:
            return  # nothing to do
        if self.interval.begin == 0:  # it is sentinel, min value is 1
            self.interval = self.Interval(row, max(self.interval.end, row))
        self.interval = self.Interval(min(self.interval.begin, row),
                                      max(self.interval.end, row))

    def add_value_to_stats(self, value):
        new_stats = self.Stats(self.stats.points + 1, [])
        stats = []
        for level in range(ColumnAnalyzer.N_LEVELS):
            ca = ColumnAnalyzer([value], level=level)

            if len(self.stats.stats) > level:
                temp = self.stats.stats[level]
            else:
                temp = {}

            for pattern, occurances in ca.patterns_dict.items():
                if pattern in temp:
                    temp[pattern][0] += occurances
                else:
                    # occurances, correct, incorrect
                    temp[pattern] = [occurances, 0, 0]
            new_stats.stats.append(temp)
        self.stats = new_stats

    def record_unmarked(self, value):
        for level in range(ColumnAnalyzer.N_LEVELS):
            ca = ColumnAnalyzer([], level)
            pattern = ca.get_pattern(value, level)
            self.stats.stats[level][pattern][1] += 1  # correct

    def record_corrected(self, value, prev_value):
        for level in range(ColumnAnalyzer.N_LEVELS):
            ca = ColumnAnalyzer([], level)
            pattern_was = ca.get_pattern(prev_value, level)
            self.stats.stats[level][pattern_was][2] += 1  # incorrect
            pattern_now = ca.get_pattern(value, level)
            if pattern_now in self.stats.stats[level]:
                self.stats.stats[level][pattern_now][1] += 1  # correct
            else:  # yet unseen pattern
                self.stats.stats[level][pattern_now] = [1, 1, 0]  # correct

    def check(self, value):
        decision = -1  # by default we do not know
        # within each layer we observe categorical distribution
        # usually one needs the number of data points n >= 10*k,
        # where k is the number of bins (patterns per layer)
        # however, we will always use layers 0 and 1
        for level in range(ColumnAnalyzer.N_LEVELS):
            if level < 2 or \
                    self.stats.points >= 10 * len(self.stats.stats[level]):
                ca = ColumnAnalyzer([], level)
                pattern = ca.get_pattern(value, level)
                if pattern not in self.stats.stats[level]:  # new pattern
                    # TODO should not ever happen:
                    #      check_old was called for a new value
                    decision = 0
                    continue
                # occurances of the pattern
                np = self.stats.stats[level][pattern][0]
                # correct occurances
                rp = self.stats.stats[level][pattern][1]
                # incorrect occurances
                wp = self.stats.stats[level][pattern][2]
                if rp > 0 and wp > 0:
                    # can say nothing on this level, need to go further
                    decision = -1
                    continue
                if rp > 0 and wp == 0:
                    # probably right, but maybe not enough stats
                    decision = 1
                if rp == 0 and wp > 0:
                    # probably wrong, but maybe not enough stats
                    decision = 0
                if rp == 0 and wp == 0:
                    # TODO test H_0: np/n_points == 0,
                    #      using some confivence interval,
                    # TODO if it crosses zero -
                    #      cannot reject H_0, => maybe wrong
                    # TODO tried Wilson confint, but it did not work
                    confidence = float(np)/self.stats.points
                    if confidence < self.BINOM_THRESHOLD:
                        decision = 0
                    elif confidence > 1.0 - self.BINOM_THRESHOLD:
                        decision = 1
                    else:
                        decision = -1
        return decision

    def make_action_request(self, event, context):
        range_name = "$%s$%%s:$%s$%%s" % (self.column, self.column)
        min_row = int(min(context.lookup(event.sheet).get_header_rows())) + 1
        if self.interval.begin <= min_row:
            begin = self.interval.end + 1
        else:
            begin = min_row
        end = begin + self.MIN_POINTS_READY - 1
        return Action.request_from_event(event, range_name % (begin, end))

    def make_action_change(self, event, cells):
        return Action.change_from_event(event, [cells])

    @staticmethod
    def apply_format(cell, **format):
        result = copy.deepcopy(cell)
        for key, value in format.iteritems():
            setattr(result, key, value)
        return result

    @staticmethod
    def match_format(cell, **format):
        for key, value in format.iteritems():
            if getattr(cell, key) != value:
                return False
        return True
