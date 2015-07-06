import unittest
import pytest
import random
import string
import json

from comnsense_agent.data import ActionError, Action, Cell
from .common import get_random_sheet_name, get_random_workbook_id
from .common import get_random_table, get_random_cell_key


class TestAction(unittest.TestCase):
    def test_init_change_cell(self):
        workbook = get_random_workbook_id()
        sheet = get_random_sheet_name()
        action = Action(Action.Type.ChangeCell, workbook, sheet)
        self.assertEquals(action.type, Action.Type.ChangeCell)
        self.assertEquals(action.workbook, workbook)
        self.assertEquals(action.sheet, sheet)
        self.assertEquals(action.cells, [])
        self.assertEquals(action.range_name, None)
        self.assertEquals(action.flags, 0)
        cells = get_random_table(10, 10)
        action = Action(Action.Type.ChangeCell, workbook, sheet, cells)
        self.assertEquals(action.type, Action.Type.ChangeCell)
        self.assertEquals(action.workbook, workbook)
        self.assertEquals(action.sheet, sheet)
        self.assertEquals(action.cells, cells)
        self.assertEquals(action.range_name, None)
        self.assertEquals(action.flags, 0)

    def test_cells(self):
        workbook = get_random_workbook_id()
        sheet = get_random_sheet_name()
        action = Action(Action.Type.ChangeCell, workbook, sheet)
        self.assertEquals(action.cells, [])
        cells = get_random_table(10, 10)
        action.cells = cells
        self.assertEquals(action.cells, cells)
        with pytest.raises(ActionError):
            action.cells = "A1:A10"
        with pytest.raises(ActionError):
            action.range_name = "A1:A10"

    def test_init_range_request(self):
        workbook = get_random_workbook_id()
        sheet = get_random_sheet_name()
        action = Action(Action.Type.RangeRequest, workbook, sheet)
        self.assertEquals(action.type, Action.Type.RangeRequest)
        self.assertEquals(action.workbook, workbook)
        self.assertEquals(action.sheet, sheet)
        self.assertEquals(action.cells, None)
        self.assertEquals(action.range_name, "")
        self.assertEquals(action.flags, 0)
        range_name = "%s:%s" % (get_random_cell_key(), get_random_cell_key())
        action = Action(Action.Type.RangeRequest, workbook, sheet, range_name)
        self.assertEquals(action.type, Action.Type.RangeRequest)
        self.assertEquals(action.workbook, workbook)
        self.assertEquals(action.sheet, sheet)
        self.assertEquals(action.cells, None)
        self.assertEquals(action.range_name, range_name)
        self.assertEquals(action.flags, 0)

    def test_range_name(self):
        workbook = get_random_workbook_id()
        sheet = get_random_sheet_name()
        action = Action(Action.Type.RangeRequest, workbook, sheet)
        self.assertEquals(action.range_name, "")
        range_name = "%s:%s" % (get_random_cell_key(), get_random_cell_key())
        action.range_name = range_name
        self.assertEquals(action.range_name, range_name)
        with pytest.raises(ActionError):
            action.range_name = []
        with pytest.raises(ActionError):
            action.cells = []

    def test_change(self):
        workbook = get_random_workbook_id()
        sheet = get_random_sheet_name()
        cells = get_random_table(10, 10)
        action = Action.change(workbook, sheet, cells)
        self.assertEquals(action.type, Action.Type.ChangeCell)
        self.assertEquals(action.workbook, workbook)
        self.assertEquals(action.sheet, sheet)
        self.assertEquals(action.cells, cells)
        self.assertEquals(action.range_name, None)
        self.assertEquals(action.flags, 0)
        flags = random.randint(0, 15)
        action = Action.change(workbook, sheet, cells, flags)
        self.assertEquals(action.type, Action.Type.ChangeCell)
        self.assertEquals(action.workbook, workbook)
        self.assertEquals(action.sheet, sheet)
        self.assertEquals(action.cells, cells)
        self.assertEquals(action.range_name, None)
        self.assertEquals(action.flags, flags)

    def test_request(self):
        workbook = get_random_workbook_id()
        sheet = get_random_sheet_name()
        range_name = "%s:%s" % (get_random_cell_key(), get_random_cell_key())
        action = Action.request(workbook, sheet, range_name)
        self.assertEquals(action.type, Action.Type.RangeRequest)
        self.assertEquals(action.workbook, workbook)
        self.assertEquals(action.sheet, sheet)
        self.assertEquals(action.cells, None)
        self.assertEquals(action.range_name, range_name)
        self.assertEquals(action.flags, 0)
        flags = random.randint(0, 15)
        action = Action.request(workbook, sheet, range_name, flags)
        self.assertEquals(action.type, Action.Type.RangeRequest)
        self.assertEquals(action.workbook, workbook)
        self.assertEquals(action.sheet, sheet)
        self.assertEquals(action.cells, None)
        self.assertEquals(action.range_name, range_name)
        self.assertEquals(action.flags, flags)

    def test_serialization_change(self):
        workbook = get_random_workbook_id()
        sheet = get_random_sheet_name()
        cells = get_random_table(10, 10)
        action = Action.change(workbook, sheet, cells)
        fixture = json.dumps(
            {"type": 0,
             "workbook": workbook,
             "sheet": sheet,
             "cells": Cell.table_to_primitive(cells)
             })
        self.assertEquals(action.serialize(), fixture)
        another = Action.deserialize(fixture)
        self.assertEquals(action, another)

    def test_serialization_change_with_flags(self):
        workbook = get_random_workbook_id()
        sheet = get_random_sheet_name()
        cells = get_random_table(10, 10)
        flags = random.randint(1, 15)
        action = Action.change(workbook, sheet, cells, flags)
        fixture = json.dumps(
            {"type": 0,
             "workbook": workbook,
             "sheet": sheet,
             "cells": Cell.table_to_primitive(cells),
             "flags": flags
             })
        self.assertEquals(action.serialize(), fixture)
        another = Action.deserialize(fixture)
        self.assertEquals(action, another)

    def test_serialization_request(self):
        workbook = get_random_workbook_id()
        sheet = get_random_sheet_name()
        range_name = "%s:%s" % (get_random_cell_key(), get_random_cell_key())
        action = Action.request(workbook, sheet, range_name)
        fixture = json.dumps(
            {"type": 1,
             "workbook": workbook,
             "sheet": sheet,
             "rangeName": range_name
             })
        self.assertEquals(action.serialize(), fixture)
        another = Action.deserialize(fixture)
        self.assertEquals(action, another)

    def test_serialization_request_with_flags(self):
        workbook = get_random_workbook_id()
        sheet = get_random_sheet_name()
        range_name = "%s:%s" % (get_random_cell_key(), get_random_cell_key())
        flags = random.randint(1, 15)
        action = Action.request(workbook, sheet, range_name, flags)
        fixture = json.dumps(
            {"type": 1,
             "workbook": workbook,
             "sheet": sheet,
             "rangeName": range_name,
             "flags": flags
             })
        self.assertEquals(action.serialize(), fixture)
        another = Action.deserialize(fixture)
        self.assertEquals(action, another)

    def test_serialization_zero_flags(self):
        workbook = get_random_workbook_id()
        sheet = get_random_sheet_name()
        range_name = "%s:%s" % (get_random_cell_key(), get_random_cell_key())
        action = Action.request(workbook, sheet, range_name, 0)
        fixture = json.dumps(
            {"type": 1,
             "workbook": workbook,
             "sheet": sheet,
             "rangeName": range_name,
             })
        self.assertEquals(action.serialize(), fixture)
        another = Action.deserialize(fixture)
        self.assertEquals(action, another)
