import unittest
import pytest
import random
import string
import mock

from comnsense_agent.automaton.header_request import WaitingHeader
from comnsense_agent.message import Message
from comnsense_agent.data import Event
from comnsense_agent.context import Context, Sheet, Table

from .common import get_random_workbook_id, get_random_cell
from .common import get_random_sheet_name


class TestStateWaitingHeader(unittest.TestCase):
    def setUp(self):
        self.context = mock.Mock()
        self.return_state = mock.Mock()
        self.context.return_state = self.return_state

    def test_event_workbook_open(self):
        workbook = get_random_workbook_id()
        event = Event(Event.Type.WorkbookOpen, workbook)
        message = Message.event(event)
        iam = WaitingHeader()
        answer, state = iam.next(self.context, message)
        self.assertEquals(answer, None)
        self.assertEquals(state, iam)

    def test_event_workbook_close(self):
        workbook = get_random_workbook_id()
        event = Event(Event.Type.WorkbookBeforeClose, workbook)
        message = Message.event(event)
        iam = WaitingHeader()
        answer, state = iam.next(self.context, message)
        self.assertEquals(answer, None)
        self.assertEquals(state, iam)

    def test_event_sheet_change(self):
        workbook = get_random_workbook_id()
        event = Event(Event.Type.SheetChange, workbook)
        message = Message.event(event)
        iam = WaitingHeader()
        answer, state = iam.next(self.context, message)
        self.assertEquals(answer, None)
        self.assertEquals(state, iam)

    def test_event_empty_cells_range_response(self):
        workbook = get_random_workbook_id()
        sheet_name = get_random_sheet_name()
        event = Event(Event.Type.RangeResponse, workbook, sheet_name)

        self.context.sheets = {}
        sheet = Sheet(self.context, sheet_name)
        table = Table(sheet)
        sheet.tables = [table]
        self.context.sheets[sheet_name] = sheet

        cells = [[
            get_random_cell("$A$1", ""),
            get_random_cell("$B$1", ""),
            get_random_cell("$C$1", ""),
            get_random_cell("$D$1", "")]]
        event.cells = cells

        message = Message.event(event)

        iam = WaitingHeader()
        state = self.context.return_state
        answer, next_state = iam.next(self.context, message)
        self.assertEquals(answer, None)
        self.assertEquals(state, next_state)
        self.assertEquals(self.context.return_state, None)
        self.assertEquals(table.header, None)

    def test_no_empty_cells_range_response(self):
        workbook = get_random_workbook_id()
        sheet_name = get_random_sheet_name()
        event = Event(Event.Type.RangeResponse, workbook, sheet_name)

        self.context.sheets = {}
        sheet = Sheet(self.context, sheet_name)
        table = Table(sheet)
        sheet.tables = [table]
        self.context.sheets[sheet_name] = sheet

        cells = [[
            get_random_cell("$A$1", get_random_sheet_name()),
            get_random_cell("$B$1", get_random_sheet_name()),
            get_random_cell("$C$1", get_random_sheet_name()),
            get_random_cell("$D$1", get_random_sheet_name())]]
        event.cells = cells

        message = Message.event(event)

        iam = WaitingHeader()
        state = self.context.return_state
        answer, next_state = iam.next(self.context, message)
        self.assertEquals(answer, None)
        self.assertEquals(state, next_state)
        self.assertEquals(self.context.return_state, None)
        self.assertEquals(table.header, cells[0])

    def test_cells_range_response(self):
        workbook = get_random_workbook_id()
        sheet_name = get_random_sheet_name()
        event = Event(Event.Type.RangeResponse, workbook, sheet_name)

        self.context.sheets = {}
        sheet = Sheet(self.context, sheet_name)
        table = Table(sheet)
        sheet.tables = [table]
        self.context.sheets[sheet_name] = sheet

        cells = [[
            get_random_cell("$A$1", get_random_sheet_name()),
            get_random_cell("$B$1", get_random_sheet_name()),
            get_random_cell("$C$1", ""),
            get_random_cell("$D$1", get_random_sheet_name())]]
        event.cells = cells

        message = Message.event(event)

        iam = WaitingHeader()
        state = self.context.return_state
        answer, next_state = iam.next(self.context, message)
        self.assertEquals(answer, None)
        self.assertEquals(state, next_state)
        self.assertEquals(self.context.return_state, None)
        self.assertEquals(table.header, [cells[0][0], cells[0][1]])
