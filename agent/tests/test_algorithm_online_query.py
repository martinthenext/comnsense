import pytest
import unittest
import mock
import random
import string
import pickle


from .common import get_random_workbook_id, get_random_cell
from .common import get_random_sheet_name
from comnsense_agent.context import Context, Sheet, Table
from comnsense_agent.data import Event, Cell
from comnsense_agent.algorithm.laptev import OnlineQuery


class TestOnlineQuery(unittest.TestCase):
    def setUp(self):
        self.workbook = get_random_workbook_id()
        self.sheet_name = get_random_sheet_name()
        self.context = mock.Mock()
        self.context.sheets = {}
        self.sheet = Sheet(self.context, self.sheet_name)
        self.table = Table(self.sheet)
        self.sheet.tables = [self.table]
        self.context.sheets[self.sheet_name] = self.sheet

    def test_get_stats_new(self):
        alg = OnlineQuery()
        column = random.choice(string.ascii_uppercase)
        n_points, stats = alg.get_stats(self.table, column)
        self.assertEquals(n_points, 0)
        self.assertEquals(stats, [])

    def test_get_stats(self):
        alg = OnlineQuery()
        orig_stats = range(10)
        orig_n_points = 10
        column = random.choice(string.ascii_uppercase)

        self.table.stats["QueryOnline"] = \
            {column: pickle.dumps((orig_n_points, orig_stats))}
        n_points, stats = alg.get_stats(self.table, column)
        self.assertEquals(n_points, orig_n_points)
        self.assertEquals(stats, orig_stats)

    def test_save_stats(self):
        alg = OnlineQuery()
        orig_stats = range(10)
        orig_n_points = 10
        column = random.choice(string.ascii_uppercase)

        alg.save_stats(self.table, column, orig_n_points, orig_stats)
        n_points, stats = pickle.loads(self.table.stats["QueryOnline"][column])

        self.assertEquals(n_points, orig_n_points)
        self.assertEquals(stats, orig_stats)

    def test_get_data(self):
        alg = OnlineQuery()
        event = Event(Event.Type.SheetChange, self.workbook, self.sheet_name)

        cells = [
            [Cell("$A$1", "VA1"), Cell("$B$1", "VB1"), Cell("$C$1", "VC1")],
            [Cell("$A$2", "VA2"), Cell("$B$2", "VB2"), Cell("$C$2", "VC2")],
        ]
        prev_cells = [
            [Cell("$A$1", "PVA1"), Cell("$B$1", None)],
            [Cell("$A$2", "PVA2"), Cell("$B$2", "")],
        ]
        event.cells = cells
        event.prev_cells = prev_cells

        a_data = alg.get_data(event, "A")
        self.assertEquals(
            a_data,
            [("$A$1", "VA1", "PVA1"),
             ("$A$2", "VA2", "PVA2")])

        b_data = alg.get_data(event, "B")
        self.assertEquals(
            b_data,
            [("$B$1", "VB1", None),
             ("$B$2", "VB2", "")])

        c_data = alg.get_data(event, "C")
        self.assertEquals(
            c_data,
            [("$C$1", "VC1", ""),
             ("$C$2", "VC2", "")])
