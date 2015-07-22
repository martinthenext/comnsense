import allure
import pytest
import mock
from hamcrest import *

from ..fixtures.excel import workbook, sheetname, header_range_response

from comnsense_agent.algorithm.header_detector import HeaderDetector
from comnsense_agent.data import Action, Event, Cell


FIXTURES = [("A", 0),   ("B", 1),   ("Z", 25),
            ("AA", 26), ("AZ", 51), ("ZZ", 701)]


@allure.feature("Header Detector")
@pytest.mark.parametrize("column,index", FIXTURES)
def test_get_column_from_index(column, index):
    algorithm = HeaderDetector()
    assert_that(algorithm.get_column_from_index(index), equal_to(column))


@allure.feature("Header Detector")
@pytest.mark.parametrize("column,index", FIXTURES)
def test_get_index_from_column(column, index):
    algorithm = HeaderDetector()
    assert_that(algorithm.get_index_from_column(column), equal_to(index))


FIXTURES = [("A", "B"),   ("Z", "AA"),  ("AA", "AB"),
            ("CZ", "DA"), ("ZA", "ZB"), ("ZY", "ZZ")]


@allure.feature("Header Detector")
@pytest.mark.parametrize("current_column,next_column", FIXTURES)
def test_get_next_column(current_column, next_column):
    algorithm = HeaderDetector()
    assert_that(algorithm.get_next_column(current_column),
                equal_to(next_column))


@allure.step("first event")
def header_detector_first_event(algorithm, context, workbook, sheetname):
    def get_first_event():
        event = Event(Event.Type.SheetChange,
                      workbook, sheetname,
                      [[Cell("$C$10", "X")]],
                      [[Cell("$C$10", "")]])
        return event

    event = get_first_event()
    allure.attach("event", event.serialize(), allure.attach_type.JSON)
    actions = algorithm.handle(event, context)
    assert_that(actions, has_length(1))
    action = actions[0]
    allure.attach("action", action.serialize(), allure.attach_type.JSON)
    assert_that(algorithm.get_header(), is_(none()))


@allure.feature("Header Detector")
@pytest.mark.parametrize(
    "step,blank",  [("no header", 0), ("short header", 11)])
def test_header_detector_short_header(workbook, sheetname, step, blank):
    algorithm = HeaderDetector()
    context = mock.Mock()

    header_detector_first_event(algorithm, context, workbook, sheetname)

    with allure.step(step):
        event = next(header_range_response(workbook, sheetname, blank))
        allure.attach("event", event.serialize(), allure.attach_type.JSON)
        actions = algorithm.handle(event, context)
        assert_that(actions, has_length(0))
        assert_that(algorithm.get_header(),
                    equal_to(event.cells[0][:blank]))


@allure.feature("Header Detector")
def test_header_detector_long_header(workbook, sheetname):
    algorithm = HeaderDetector()
    context = mock.Mock()

    header_detector_first_event(algorithm, context, workbook, sheetname)

    steps = ["long header", "end of header"]
    events = [next(header_range_response(workbook, sheetname, 52)),
              next(header_range_response(workbook, sheetname, 11, 52, 78))]
    actions = [1, 0]
    headers = [none(), events[0].cells[0] + events[1].cells[0][:11]]

    for step, event, action, header in zip(steps, events, actions, headers):
        with allure.step(step):
            allure.attach("event", event.serialize(),
                          allure.attach_type.JSON)
            actions = algorithm.handle(event, context)
            assert_that(actions, has_length(action))
            if action == 1:
                allure.attach("action", actions[0].serialize(),
                              allure.attach_type.JSON)
            assert_that(algorithm.get_header(), is_(header))


@allure.feature("Header Detector")
@pytest.mark.parametrize("blank,expected", [(0, 0), (11, 11), (52, -1)])
def test_get_first_empty_cell_index(workbook, sheetname, blank, expected):
    event = next(header_range_response(workbook, sheetname, blank))
    allure.attach("event", event.serialize(), allure.attach_type.JSON)
    algorithm = HeaderDetector()
    header = event.cells[0]
    index = algorithm.get_first_empty_cell_index(header)
    assert_that(index, equal_to(expected))
