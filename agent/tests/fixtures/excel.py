import pytest
import string
import random

from ..common import get_random_string, get_random_workbook_id
from ..common import get_random_sheet_name

from comnsense_agent.data import Event, Cell


@pytest.yield_fixture
def random_column():
    yield random.choice(string.ascii_uppercase)


@pytest.yield_fixture
def random_row():
    yield random.randint(1, 100)


@pytest.yield_fixture(scope="module")
def workbook():
    yield get_random_workbook_id()


@pytest.yield_fixture(scope="module")
def sheetname():
    yield get_random_sheet_name()


def columns():
    for h in [None] + list(string.ascii_uppercase):
        for l in list(string.ascii_uppercase):
            if h is None:
                yield l
            else:
                yield h + l


@pytest.yield_fixture
def header_range_response(workbook, sheetname, blank=10, start=0, end=52):
    cells = [Cell("$%s$1" % x, "" if i >= blank else get_random_string())
             for i, x in enumerate(list(columns())[start:end])]
    event = Event(Event.Type.RangeResponse,
                  workbook, sheetname, [cells])
    yield event


@pytest.yield_fixture
def range_response(workbook, sheetname, key, value):
    event = Event(Event.Type.RangeResponse,
                  workbook, sheetname,
                  [[Cell(key, value)]])
    yield event


@pytest.yield_fixture
def random_range_response(workbook, sheetname):
    key = "$%s$%s" % (next(random_column()), next(random_row()))
    value = get_random_string()
    yield next(range_response(workbook, sheetname, key, value))


@pytest.yield_fixture
def random_sheet_change(workbook, sheetname):
    key = "$%s$%s" % (next(random_column()), next(random_row()))
    event = Event(Event.Type.SheetChange,
                  workbook, sheetname,
                  [[Cell(key, get_random_string())]],
                  [[Cell(key, get_random_string())]])
    yield event


@pytest.yield_fixture
def sheet_change(workbook, sheetname, key, value, prev_value=""):
    event = Event(Event.Type.SheetChange,
                  workbook, sheetname,
                  [[Cell(key, value)]],
                  [[Cell(key, prev_value)]])
    yield event


@pytest.yield_fixture
def before_close(workbook):
    event = Event(Event.Type.WorkbookBeforeClose, workbook)
    yield event


@pytest.yield_fixture
def workbook_open(workbook):
    event = Event(Event.Type.WorkbookOpen, workbook)
    yield event
