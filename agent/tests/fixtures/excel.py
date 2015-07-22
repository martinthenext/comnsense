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


@pytest.yield_fixture
def workbook():
    yield get_random_workbook_id()


@pytest.yield_fixture
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
