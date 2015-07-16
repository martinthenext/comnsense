import pytest
import unittest
import mock
import random

from comnsense_agent.automaton import State
from comnsense_agent.automaton.header_request import WaitingHeader
from comnsense_agent.automaton.ready import Ready
from comnsense_agent.context import Sheet, Table
from comnsense_agent.data import Event, Action, Signal
from comnsense_agent.message import Message, MESSAGE_ACTION

from .common import get_random_sheet_name
from .common import get_random_cell
from .common import get_random_workbook_id


class TestStateReady(unittest.TestCase):
    def setUp(self):
        self.context = mock.Mock()
        self.return_state = mock.Mock()
        self.context.return_state = self.return_state
        self.context.sheets = {}
        self.algorithm = mock.Mock()
        self.algorithm.query.return_value = None

    def set_header(self, sheet_name):
        header = [
            get_random_cell("$A$1", get_random_sheet_name()),
            get_random_cell("$B$1", get_random_sheet_name()),
            get_random_cell("$C$1", "")]
        self.context.sheets[sheet_name].tables[0].header = header
        return header

    def set_sheet(self, sheet_name):
        sheet = Sheet(self.context, sheet_name)
        table = Table(sheet)
        sheet.tables.append(table)
        self.context.sheets = {sheet_name: sheet}
        return sheet

    def test_event_workbook_open_without_header(self):
        workbook = get_random_workbook_id()
        sheet_name = get_random_sheet_name()
        self.context.workbook = workbook
        event = Event(Event.Type.WorkbookOpen, workbook, sheet_name)

        Ready.algorithm = self.algorithm
        iam = Ready()
        message, state = iam.next(self.context, Message.event(event))

        self.assertEquals(message.kind, MESSAGE_ACTION)
        self.assertEquals(state.__class__, WaitingHeader)

    def test_event_workbook_open_with_header(self):
        workbook = get_random_workbook_id()
        sheet_name = get_random_sheet_name()
        self.context.workbook = workbook
        sheet = self.set_sheet(sheet_name)
        header = self.set_header(sheet_name)
        event = Event(Event.Type.WorkbookOpen, workbook, sheet_name)

        Ready.algorithm = self.algorithm
        iam = Ready()
        message, state = iam.next(self.context, Message.event(event))

        self.assertEquals(message, None)
        self.assertEquals(state, iam)

    def test_event_range_response_without_header(self):
        workbook = get_random_workbook_id()
        sheet_name = get_random_sheet_name()
        self.context.workbook = workbook
        cells = [[
            get_random_cell("$A$1", get_random_sheet_name()),
            get_random_cell("$B$1", get_random_sheet_name())]]
        event = Event(Event.Type.RangeResponse, workbook, sheet_name, cells)

        Ready.algorithm = self.algorithm
        iam = Ready()
        message, state = iam.next(self.context, Message.event(event))

        self.assertEquals(message.kind, MESSAGE_ACTION)
        self.assertEquals(state.__class__, WaitingHeader)

    def test_event_range_response_with_header(self):
        workbook = get_random_workbook_id()
        sheet_name = get_random_sheet_name()
        self.context.workbook = workbook
        sheet = self.set_sheet(sheet_name)
        header = self.set_header(sheet_name)
        cells = [[
            get_random_cell("$A$1", get_random_sheet_name()),
            get_random_cell("$B$1", get_random_sheet_name())]]
        event = Event(Event.Type.RangeResponse, workbook, sheet_name, cells)

        Ready.algorithm = self.algorithm
        iam = Ready()
        message, state = iam.next(self.context, Message.event(event))

        self.assertEquals(message, None)
        self.assertEquals(state, iam)
        self.assertEquals(len(self.algorithm.query.mock_calls), 1)
        kall = self.algorithm.query.mock_calls[0]
        self.assertEquals(kall[1][0], self.context)
        self.assertEquals(kall[1][1], event)

    def test_event_sheet_change_without_header(self):
        workbook = get_random_workbook_id()
        sheet_name = get_random_sheet_name()
        self.context.workbook = workbook
        cells = [[
            get_random_cell("$A$1", get_random_sheet_name()),
            get_random_cell("$B$1", get_random_sheet_name())]]
        event = Event(Event.Type.SheetChange, workbook, sheet_name, cells)

        Ready.algorithm = self.algorithm
        iam = Ready()
        message, state = iam.next(self.context, Message.event(event))

        self.assertEquals(message.kind, MESSAGE_ACTION)
        self.assertEquals(state.__class__, WaitingHeader)

    def test_event_sheet_change_with_header(self):
        workbook = get_random_workbook_id()
        sheet_name = get_random_sheet_name()
        self.context.workbook = workbook
        sheet = self.set_sheet(sheet_name)
        header = self.set_header(sheet_name)
        cells = [[
            get_random_cell("$A$1", get_random_sheet_name()),
            get_random_cell("$B$1", get_random_sheet_name())]]
        event = Event(Event.Type.SheetChange, workbook, sheet_name, cells)

        Ready.algorithm = self.algorithm
        iam = Ready()
        message, state = iam.next(self.context, Message.event(event))

        self.assertEquals(message, None)
        self.assertEquals(state, iam)
        self.assertEquals(len(self.algorithm.query.mock_calls), 1)
        kall = self.algorithm.query.mock_calls[0]
        self.assertEquals(kall[1][0], self.context)
        self.assertEquals(kall[1][1], event)

    def test_event_before_close_without_header(self):
        workbook = get_random_workbook_id()
        sheet_name = get_random_sheet_name()
        self.context.workbook = workbook
        event = Event(Event.Type.WorkbookBeforeClose, workbook, sheet_name)

        Ready.algorithm = self.algorithm
        iam = Ready()
        message, state = iam.next(self.context, Message.event(event))

        self.assertEquals(message, None)
        self.assertEquals(state, None)

    def test_event_before_close_with_header(self):
        workbook = get_random_workbook_id()
        sheet_name = get_random_sheet_name()
        self.context.workbook = workbook
        sheet = self.set_sheet(sheet_name)
        header = self.set_header(sheet_name)
        event = Event(Event.Type.WorkbookBeforeClose, workbook, sheet_name)

        Ready.algorithm = self.algorithm
        iam = Ready()
        message, state = iam.next(self.context, Message.event(event))

        self.assertEquals(message, None)
        self.assertEquals(state, None)

    def test_no_event(self):
        req = Message.signal(Signal.ready())

        Ready.algorithm = self.algorithm
        iam = Ready()
        message, state = iam.next(self.context, req)

        self.assertEquals(message, None)
        self.assertEquals(state, iam)
