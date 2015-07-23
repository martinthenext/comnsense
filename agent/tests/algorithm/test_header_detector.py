import allure
import pytest
import mock
from functools import partial
from hamcrest import *

from ..fixtures.excel import workbook, sheetname, header_range_response
from ..fixtures.excel import random_sheet_change

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


FIXTURES = [(["no header"], [0]),
            (["short header"], [10]),
            (["long header", "end of header"], [52, 10])]


@allure.feature("Header Detector")
@pytest.mark.parametrize("steps, blanks", FIXTURES,
                         ids=["no header", "short header", "long header"])
def test_header_detector_detect(workbook, sheetname, steps, blanks):
    algorithm = HeaderDetector()
    context = mock.Mock()

    def check(event, length, header):
        allure.attach("event", event.serialize(), allure.attach_type.JSON)
        actions = algorithm.handle(event, context)
        assert_that(actions, has_length(length))
        if length == 1:
            action = actions[0]
            allure.attach("action", action.serialize(),
                          allure.attach_type.JSON)
        assert_that(algorithm.get_header(), is_(header))

    with allure.step("first step"):
        event = next(random_sheet_change(workbook, sheetname))
        check(event, 1, none())

    collected = []
    for i, (step, blank) in enumerate(zip(steps, blanks)):
        event = next(header_range_response(workbook, sheetname,
                                           start=(i * 52), blank=blank,
                                           end=(i + 1) * 52 - i * 26))
        if i == len(steps) - 1:
            length = 0
            header = collected + event.cells[0][:blank]
        else:
            length = 1
            header = none()
            collected += event.cells[0]
        with allure.step(step):
            check(event, length, header)


@allure.feature("Header Detector")
@pytest.mark.parametrize("blank,expected", [(0, 0), (11, 11), (52, -1)])
def test_get_first_empty_cell_index(workbook, sheetname, blank, expected):
    event = next(header_range_response(workbook, sheetname, blank))
    allure.attach("event", event.serialize(), allure.attach_type.JSON)
    algorithm = HeaderDetector()
    header = event.cells[0]
    index = algorithm.get_first_empty_cell_index(header)
    assert_that(index, equal_to(expected))
