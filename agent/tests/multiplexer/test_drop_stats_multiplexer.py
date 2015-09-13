import allure
import pytest
import mock
from hamcrest import *

from ..fixtures.excel import workbook_open, before_close
from ..fixtures.excel import workbook, sheetname

from comnsense_agent.data import Action, Event, Cell

from comnsense_agent.multiplexer.drop_stats_multiplexer \
    import DropStatsMultiplexer


@pytest.yield_fixture
def handler():
    yield mock.Mock()


@pytest.yield_fixture
def context(handler):
    context = mock.Mock()
    context.lookup.return_value = handler
    yield context


@pytest.yield_fixture
def mux(context):
    multiplexer = DropStatsMultiplexer(context)
    yield multiplexer


@pytest.fixture
def event(workbook, sheetname):
    return Event(Event.Type.SheetChange, workbook, sheetname,
                 [[Cell("$A$1", "value")]])


@pytest.fixture
def answer(event, request):
    if request.param == "no changes":
        return [
            Action.request_from_event(event, "$A$1"),
            Action.request_from_event(event, "$A$2")]

    if request.param == "no value changes":
        cell = event.cells[0][0]
        return [Action.change_from_event(
                    event, [[Cell(cell.key, cell.value, color=3)]]),
                Action.request_from_event(event, "$A$1")]

    if request.param == "changes":
        cell = event.cells[0][0]
        return [Action.change_from_event(
                    event, [[Cell(cell.key, cell.value, color=3),
                             Cell("$S$8", "changed")]]),
                Action.request_from_event(event, "$S$9")]


@allure.feature("Multiplexer")
@pytest.mark.parametrize(
    "answer", ["no changes", "no value changes", "changes"], indirect=True)
def test_invalidate_workbook_open(mux, handler, workbook_open, answer):
    answer = mux._invalidate(workbook_open, answer)
    assert_that(handler.invalidate.mock_calls, empty())


@allure.feature("Multiplexer")
@pytest.mark.parametrize(
    "answer", ["no changes", "no value changes", "changes"], indirect=True)
def test_invalidate_before_close(mux, handler, before_close, answer):
    answer = mux._invalidate(before_close, answer)
    assert_that(handler.invalidate.mock_calls, empty())


@allure.feature("Multiplexer")
@pytest.mark.parametrize(
    "answer", ["no changes", "no value changes"], indirect=True)
def test_invalidate_no_value_changes(mux, handler, event, answer):
    answer = mux._invalidate(event, answer)
    assert_that(handler.invalidate.mock_calls, empty())


@allure.feature("Multiplexer")
@pytest.mark.parametrize("answer", ["changes"], indirect=True)
def test_invalidate_value_changes(mux, handler, event, answer):
    answer = mux._invalidate(event, answer)
    assert_that(handler.invalidate.mock_calls,
                equal_to([mock.call([[Cell("$S$8", "changed")]])]))
