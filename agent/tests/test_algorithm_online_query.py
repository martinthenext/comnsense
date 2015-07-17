# encoding=utf-8
import pytest
import unittest
import mock
import random
import string
import pickle
import allure
import json
from collections import namedtuple
from hamcrest import *


from .common import get_random_workbook_id, get_random_cell
from .common import get_random_sheet_name
from comnsense_agent.context import Context, Sheet, Table
from comnsense_agent.data import Event, Cell
from comnsense_agent.algorithm.laptev import OnlineQuery


def get_blank_context(workbook, sheetname):
    context = mock.Mock()
    context.sheets = {}
    sheet = Sheet(context, sheetname)
    table = Table(sheet)
    sheet.tables = [table]
    context.sheets[sheetname] = sheet
    return context


def get_random_lowercase_ascii_string():
    max_length = 10
    min_length = 1
    length = random.randint(min_length, max_length)
    result = "".join(random.sample(string.ascii_lowercase, length))
    return result


@pytest.yield_fixture
def workbook():
    yield get_random_workbook_id()


@pytest.yield_fixture
def sheetname():
    yield get_random_sheet_name()


def test_algorithm_on_blank_sheet(workbook, sheetname):
    """
        Case:
            creating column with english latters on empty sheet
    """
    allure.attach("workbook", workbook)
    allure.attach("sheetname", sheetname)

    algorithm = OnlineQuery()

    column = "A"
    event_count = 5

    def get_event(num, value=None):
        key = "$%s$%d" % (column, num)
        if value is None:
            value = get_random_lowercase_ascii_string()
        cells = [[Cell(key, value)]]
        prev_cells = [[Cell(key, "")]]
        event = Event(Event.Type.SheetChange, workbook,
                      sheetname, cells, prev_cells)
        allure.attach("event", event.serialize(),
                      type=allure.attach_type.JSON)
        return event

    def get_stats(context):
        table = context.sheets[sheetname].tables[0]
        n_points, stats = algorithm.get_stats(table, column)
        allure.attach("n_points", str(n_points))
        allure.attach("stats", json.dumps(stats, indent=2),
                      allure.attach_type.JSON)
        return n_points, stats

    with allure.step("create blank context"):
        context = get_blank_context(workbook, sheetname)

    for num in range(1, event_count + 1):
        with allure.step("send event: %d" % num):
            event = get_event(num)
            action = algorithm.query(context, event)
            n_points, stats = get_stats(context)
            assert_that(action, none())

    with allure.step("send wrong event"):
        event = get_event(event_count + 1, "1")
        action = algorithm.query(context, event)
        n_points, stats = get_stats(context)
        assert_that(action, not_none())


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

        self.table.stats["OnlineQuery"] = \
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
        n_points, stats = pickle.loads(self.table.stats["OnlineQuery"][column])

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

    def test_get_action_no_stats(self):
        pass
