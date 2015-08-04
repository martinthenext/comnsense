import allure
import pytest
import string

from comnsense_agent.data import Event, Cell, Action


class Scenario(object):
    def __init__(self, workbook):
        self.workbook = workbook
        self.steps = []
        self.actions = 0

    def open(self, comment=None):
        event = Event(Event.Type.WorkbookOpen, self.workbook.identity)

        def step():
            return event, comment

        self.steps.append(step)

    def close(self, comment=None):
        event = Event(Event.Type.WorkbookBeforeClose, self.workbook.identity)

        def step():
            return event, comment

        self.steps.append(step)

    def change(self, sheet, key, value, comment=None, **kwargs):
        def step():
            prev_value = self.workbook.get(sheet, key).value
            event = Event(Event.Type.SheetChange,
                          self.workbook.identity,
                          sheet,
                          [[Cell(key, value, **kwargs)]],
                          [[Cell(key, prev_value)]])
            self.workbook.put(sheet, Cell(key, value, **kwargs))
            return event, comment

        self.steps.append(step)

    def apply(self, action):
        event = None
        with allure.step("action: %d" % self.actions):
            self.actions += 1

            if action.type == Action.Type.ChangeCell:
                for row in action.cells:
                    for cell in row:
                        self.workbook.put(action.sheet, cell)

            elif action.type == Action.Type.RangeRequest:
                cols, rows = self._parse_range_name(action.range_name)
                cells = []
                for row_number in rows:
                    row = []
                    for col_number in cols:
                        row.append(self.workbook.get(
                            action.sheet, "$%s$%s" % (col_number, row_number)))
                    cells.append(row)
                event = Event(Event.Type.RangeResponse, self.workbook.identity,
                              action.sheet, cells)

            allure.attach("action", action.serialize())
            allure.attach("workbook.%s" % action.sheet,
                          self.workbook.serialize(action.sheet))
        if event:
            allure.attach("answer", event.serialize())
            return event

    def _parse_range_name(self, range_name):
        if ":" in range_name:
            left, right = range_name.split(":")
            _, left_col, left_row = left.split("$")
            _, right_col, right_row = right.split("$")
            rows = map(str, xrange(int(left_row), int(right_row) + 1))
            left_col = string.ascii_uppercase.index(left_col)
            right_col = string.ascii_uppercase.index(right_col)
            cols = map(lambda x: string.ascii_uppercase[x],
                       xrange(left_col, right_col + 1))
            return cols, rows
        else:
            _, col, row = range_name.split("$")
            return [col], [row]

    def __iter__(self):
        for i, step in enumerate(self.steps):
            event, comment = step()
            if comment is None:
                comment = "step %d" % i
            with allure.step(comment):
                for sheet in self.workbook.sheets():
                    allure.attach("workbook.%s" % sheet,
                                  self.workbook.serialize(sheet))
                allure.attach("event", event.serialize())
                yield event
