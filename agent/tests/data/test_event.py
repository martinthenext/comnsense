import allure
import pytest
from hamcrest import *

from ..fixtures.excel import workbook, sheetname

from comnsense_agent.data import Event
from comnsense_agent.data import Cell
from comnsense_agent.data.data import Data


@allure.feature("Data")
@pytest.mark.parametrize("type", [1, 1.0, "str"])
def test_event_incorrect_type(type, workbook):
    with pytest.raises(Data.ValidationError):
        Event(type, workbook)


FIXTURES = [
    (Event.Type.WorkbookOpen, None),
    (Event.Type.WorkbookBeforeClose, None),
    (Event.Type.SheetChange, Data.ValidationError),
    (Event.Type.RangeResponse, Data.ValidationError)]
IDS = ["WorkbookOpen",
       "WorkbookBeforeClose",
       "SheetChange",
       "RangeResponse"]


@allure.feature("Data")
@pytest.mark.parametrize("type, _", FIXTURES, ids=IDS)
@pytest.mark.parametrize("workbook", ["", None])
def test_event_no_workbook(type, workbook, _):
    with pytest.raises(Data.ValidationError):
        Event(type, workbook)


@allure.feature("Data")
@pytest.mark.parametrize("type, expected", FIXTURES, ids=IDS)
def test_event_no_sheet(type, workbook, expected):
    if expected:
        with pytest.raises(expected):
            Event(type, workbook)
    else:
        event = Event(type, workbook)
        assert_that(event.type, equal_to(type))
        assert_that(event.workbook, equal_to(workbook))
        assert_that(event.sheet, is_(none()))
        assert_that(event.cells, is_(none()))
        assert_that(event.prev_cells, is_(none()))


@allure.feature("Data")
@pytest.mark.parametrize("type, expected", FIXTURES, ids=IDS)
def test_event_no_cells(type, workbook, sheetname, expected):
    if expected:
        with pytest.raises(expected):
            Event(type, workbook, sheetname)
    else:
        event = Event(type, workbook, sheetname)
        assert_that(event.type, equal_to(type))
        assert_that(event.workbook, equal_to(workbook))
        assert_that(event.sheet, is_(none()))
        assert_that(event.cells, is_(none()))
        assert_that(event.prev_cells, is_(none()))


FIXTURES = [
    ([[]], {}),
    ([[Cell("$A$1", "")]],
     {"1": [Cell("$A$1", "")]}),
    ([[Cell("$A$1", "")], [Cell("$B$2", "")]],
     {"1": [Cell("$A$1", "")], "2": [Cell("$B$2", "")]}),
    ([[Cell("$A$1", ""), Cell("$B$2", "")]],
     {"1": [Cell("$A$1", "")], "2": [Cell("$B$2", "")]})]


@allure.feature("Data")
@pytest.mark.parametrize("type", [Event.Type.SheetChange,
                                  Event.Type.RangeResponse])
@pytest.mark.parametrize("cells, expected", FIXTURES)
def test_event_rows(type, workbook, sheetname, cells, expected):
    event = Event(type, workbook, sheetname, cells)
    assert_that(event.rows, equal_to(expected))


@allure.feature("Data")
@pytest.mark.parametrize("type", [Event.Type.SheetChange])
@pytest.mark.parametrize("cells, expected", FIXTURES)
def test_event_change_prev_rows(type, workbook, sheetname, cells, expected):
    event = Event(type, workbook, sheetname, [[]], cells)
    assert_that(event.prev_rows, equal_to(expected))


@allure.feature("Data")
@pytest.mark.parametrize("type", [Event.Type.RangeResponse])
@pytest.mark.parametrize("cells, expected", FIXTURES)
def test_event_response_prev_rows(type, workbook, sheetname, cells, expected):
    event = Event(type, workbook, sheetname, [[]], cells)
    assert_that(event.prev_rows, equal_to({}))


FIXTURES = [
    ([[]], {}),
    ([[Cell("$A$1", "")]],
     {"A": [Cell("$A$1", "")]}),
    ([[Cell("$A$1", "")], [Cell("$B$2", "")]],
     {"A": [Cell("$A$1", "")], "B": [Cell("$B$2", "")]}),
    ([[Cell("$A$1", ""), Cell("$B$2", "")]],
     {"A": [Cell("$A$1", "")], "B": [Cell("$B$2", "")]})]


@allure.feature("Data")
@pytest.mark.parametrize("type", [Event.Type.SheetChange,
                                  Event.Type.RangeResponse])
@pytest.mark.parametrize("cells, expected", FIXTURES)
def test_event_columns(type, workbook, sheetname, cells, expected):
    event = Event(type, workbook, sheetname, cells)
    assert_that(event.columns, equal_to(expected))


@allure.feature("Data")
@pytest.mark.parametrize("type", [Event.Type.SheetChange])
@pytest.mark.parametrize("cells, expected", FIXTURES)
def test_event_change_prev_columns(type, workbook, sheetname, cells, expected):
    event = Event(type, workbook, sheetname, [[]], cells)
    assert_that(event.prev_columns, equal_to(expected))


@allure.feature("Data")
@pytest.mark.parametrize("type", [Event.Type.RangeResponse])
@pytest.mark.parametrize("cells, expected", FIXTURES)
def test_event_response_prev_columns(type, workbook, sheetname,
                                     cells, expected):
    event = Event(type, workbook, sheetname, [[]], cells)
    assert_that(event.prev_columns, equal_to({}))


@allure.feature("Data")
@pytest.mark.parametrize("type", [Event.Type.WorkbookOpen,
                                  Event.Type.WorkbookBeforeClose,
                                  Event.Type.SheetChange,
                                  Event.Type.RangeResponse])
@pytest.mark.parametrize("cells", [[[]], [[Cell("$A$1", "")]]])
def test_event_repr(type, workbook, sheetname, cells):
    event = Event(type, workbook, sheetname, cells)
    allure.attach("repr", repr(event))
    allure.attach("str", str(event))


CELLS = [
    [[]],
    [[Cell("$A$1", "")]],
    [[Cell("$A$1", "")], [Cell("$B$2", "")]],
    [[Cell("$A$1", ""), Cell("$B$2", "")]]]


@allure.feature("Data")
@pytest.mark.parametrize("type", [Event.Type.WorkbookOpen,
                                  Event.Type.WorkbookBeforeClose,
                                  Event.Type.SheetChange,
                                  Event.Type.RangeResponse])
@pytest.mark.parametrize("cells", CELLS)
@pytest.mark.parametrize("prev_cells", CELLS)
def test_event_serialization(type, workbook, sheetname, cells, prev_cells):
    event = Event(type, workbook, sheetname, cells, prev_cells)
    serialized = event.serialize()
    allure.attach("serialized", serialized, allure.attach_type.JSON)
    deserialized = Event.deserialize(serialized)
    assert_that(deserialized, equal_to(event))
