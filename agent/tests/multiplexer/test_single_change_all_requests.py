import allure
import pytest
from hamcrest import *


from ..fixtures.excel import workbook, sheetname, random_sheet_change as event

from comnsense_agent.data import Action, Cell

from comnsense_agent.multiplexer.single_change_all_requests \
    import SingleChangeAllRequests


def req(name):
    def wrapper(event):
        return Action.request_from_event(event, name)
    return wrapper


def cng(*keys):
    def wrapper(event):
        return Action.change_from_event(
            event, [[Cell(key, "") for key in keys]])
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
    ([[req("$A$1:$A$10")],
      [req("$B$1:$B$A10")]], [req("$A$1:$A$10"),
                              req("$B$1:$B$A10")]),
    ([[], [req("$B$1:$B$10")]], [req("$B$1:$B$10")]),
    ([None, [req("$B$1:$B$10")]], [req("$B$1:$B$10")]),
    ([[cng("$A$1")],
      [cng("$A$2")],
      [cng("$A$3")]], [cng("$A$1", "$A$2", "$A$3")]),
    ([[cng("$A$1"), req("$A$2")],
      [cng("$B$1")],
      [req("$C$1")]], [cng("$A$1", "$B$1"), req("$A$2"), req("$C$1")])]


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


@allure.feature("Multiplexer")
@pytest.mark.parametrize("answers, expected", FIXTURES, indirect=True)
def test_first_answer(event, answers, expected):
    mux = SingleChangeAllRequests()
    result = mux.merge(event, answers)
    assert_that(result, contains(*expected))
