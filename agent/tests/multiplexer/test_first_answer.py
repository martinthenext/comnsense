import allure
import pytest
from hamcrest import *

from ..fixtures.excel import random_range_response, random_sheet_change
from ..fixtures.excel import workbook, sheetname, workbook_open

from comnsense_agent.data import Action

from comnsense_agent.multiplexer.first_answer import FirstAnswer


def req(name):
    def wrapper(event):
        return Action.request_from_event(event, name)
    return wrapper


FIXTURES = [
    ([],         []),
    ([[], []],   []),
    ([None],     []),
    ([None, []], []),
    ([[], None], []),
    ([[req("$A$1:$A$10")]], [req("$A$1:$A$10")]),
    ([[req("$A$1:$A$10"),
       req("$B$1:$B$10")], []], [req("$A$1:$A$10"),
                                 req("$B$1:$B$10")]),
    ([[req("$A$1:$A$10")], [req("$B$1:$B$A10")]], [req("$A$1:$A$10")]),
    ([[], [req("$B$1:$B$10")]], [req("$B$1:$B$10")]),
    ([None, [req("$B$1:$B$10")]], [req("$B$1:$B$10")])]


@pytest.yield_fixture
def answers(event, request):
    result = []
    for value in request.param:
        if value is None:
            result.append(None)
        else:
            result.append([x(event) for x in value])
    yield result


@pytest.yield_fixture
def expected(event, request):
    yield [x(event) for x in request.param]


@pytest.yield_fixture(
    scope="module",
    params=["range response", "sheet change"])
def event(workbook, sheetname, request):
    if request.param == "workbook open":
        yield next(workbook_open(workbook))
    elif request.param == "range response":
        yield next(random_range_response(workbook, sheetname))
    elif request.param == "sheet change":
        yield next(random_sheet_change(workbook, sheetname))


@allure.feature("Multiplexer")
@pytest.mark.parametrize("answers, expected", FIXTURES, indirect=True)
def test_first_answer(event, answers, expected):
    mux = FirstAnswer()
    result = mux.merge(event, answers)
    assert_that(result, contains(*expected))
