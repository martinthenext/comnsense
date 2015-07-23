import enum
import logging

from ..event_handler import EventHandler
from .feature_extractor import column_analyzer
from comnsense_agent.data import Event, Cell, Action

logger = logging.getLogger(__name__)


class OnlineQuery(EventHandler):
    N_LAYERS = 3
    # pattern occurs 10 times rarer than the average pattern
    BINOM_THRESHOLD = 0.5
    RIGHT_COLOR = 0
    WRONG_COLOR = 3

    def __init__(self):
        self.stats = {}

    @enum.unique
    class Action(enum.IntEnum):
        CheckNew = 0
        CheckOld = 1
        CellCorrected = 2
        CellUnmarked = 3

    def get_stats(self, column):
        stats = self.stats.get(column) or (0, [])
        return stats

    def save_stats(self, column, n_points, stats):
        self.stats[column] = (n_points, stats)

    def get_data(self, event, column):
        cells = event.columns.get(column, [])
        prev_cells = event.prev_columns.get(column, [None] * len(cells))
        return zip(
            [cell.key if cell else "" for cell in cells],
            [cell.value if cell else "" for cell in cells],
            [cell.value if cell else "" for cell in prev_cells])

    def get_action(self, event_type, value, prev_value, stats, n_points):
        assert event_type in (Event.Type.RangeResponse, Event.Type.SheetChange)
        action = None

        # we have no stats, always CheckNew
        if n_points == 0:
            return OnlineQuery.Action.CheckNew

        # it is response, it is definitly old data
        if event_type == Event.Type.RangeResponse:
            action = OnlineQuery.Action.CheckOld

        # no prev value, CheckNew
        if value and not prev_value:
            return OnlineQuery.Action.CheckNew

        # old value is changed, CellCorrected
        if value and prev_value:
            action = OnlineQuery.Action.CellCorrected

        for level in range(self.N_LAYERS):
            ca = column_analyzer([], level)
            pattern = ca.get_pattern(value, level)
            if pattern not in stats[level]:  # new pattern
                return OnlineQuery.Action.CheckNew

        # value deleted, CellUnmarked
        if not value and prev_value:
            return OnlineQuery.Action.CellUnmarked

        return action

    def add_value_to_stats(self, value, n_points, stats_dump):
        n_points += 1
        stats = []
        for level in range(self.N_LAYERS):
            ca = column_analyzer([value], level=level)
            temp = stats_dump[level] if len(stats_dump) > level else {}
            for (pattern, occurances) in ca.patterns_dict.items():
                if pattern in temp:
                    temp[pattern][0] += occurances
                else:
                    # occurances, correct, incorrect
                    temp[pattern] = [occurances, 0, 0]
            stats.append(temp)
        return n_points, stats

    def record_unmarked(self, value, n_points, stats):
        for level in range(self.N_LAYERS):
            ca = column_analyzer([], level)
            pattern = ca.get_pattern(value, level)
            stats[level][pattern][1] += 1  # correct
        return n_points, stats

    def record_corrected(self, value, prev_value, n_points, stats):
        for level in range(self.N_LAYERS):
            ca = column_analyzer([], level)
            pattern_was = ca.get_pattern(prev_value, level)
            stats[level][pattern_was][2] += 1  # incorrect
            pattern_now = ca.get_pattern(value, level)
            if pattern_now in stats[level]:
                stats[level][pattern_now][1] += 1  # correct
            else:  # yet unseen pattern
                stats[level][pattern_now] = [1, 1, 0]  # correct
        return n_points, stats

    def check(self, value, n_points, stats):
        decision = -1  # by default we do not know
        # within each layer we observe categorical distribution
        # usually one needs the number of data points n >= 10*k,
        # where k is the number of bins (patterns per layer)
        # however, we will always use layers 0 and 1
        for level in range(self.N_LAYERS):
            if level < 2 or n_points >= 10 * len(stats[level]):
                ca = column_analyzer([], level)
                pattern = ca.get_pattern(value, level)
                if pattern not in stats[level]:  # new pattern
                    # TODO should not ever happen:
                    #      check_old was called for a new value
                    decision = 0
                    continue
                np = stats[level][pattern][0]  # occurances of the pattern
                rp = stats[level][pattern][1]  # correct occurances
                wp = stats[level][pattern][2]  # incorrect occurances
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
                    if float(np)/n_points < self.BINOM_THRESHOLD:
                        decision = 0
                    elif float(np)/n_points > 1.0 - self.BINOM_THRESHOLD:
                        decision = 1
                    else:
                        decision = -1
        return decision

    def make_answer(self, event, cells):
        rows = {}
        if not cells:
            return
        for cell in cells:
            if cell.row in rows:
                rows[cell.row].append(cell)
            else:
                rows[cell.row] = [cell]
        return [Action.change_from_event(event, list(rows.values()))]

    def handle(self, event, context):
        answer_cells = []

        for column in event.columns:
            n_points, stats_dump = self.get_stats(column)
            data = self.get_data(event, column)

            for key, value, prev_value in data:
                action = self.get_action(event.type, value, prev_value,
                                         stats_dump, n_points)

                if action == OnlineQuery.Action.CheckNew:
                    n_points, stats = self.add_value_to_stats(
                        value, n_points, stats_dump)

                else:
                    stats = stats_dump

                if action == OnlineQuery.Action.CellUnmarked:
                    n_points, stats = self.record_unmarked(
                        value, n_points, stats)

                if action == OnlineQuery.Action.CellCorrected:
                    n_points, stats = self.record_corrected(
                        value, prev_value, n_points, stats)

                if action != OnlineQuery.Action.CheckOld:  # save dump
                    self.save_stats(column, n_points, stats)

                if action in (OnlineQuery.Action.CheckOld,
                              OnlineQuery.Action.CheckNew):
                    decision = self.check(value, n_points, stats)
                    if decision == 0:
                        answer_cells.append(
                            Cell(key, value, color=self.WRONG_COLOR))

        return self.make_answer(event, answer_cells)
