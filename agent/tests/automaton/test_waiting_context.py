import pytest
import allure
import mock
from hamcrest import *


from ..fixtures.excel import before_close, workbook, sheetname
from ..fixtures.excel import random_range_response, random_sheet_change
from ..fixtures.excel import workbook_open
from ..fixtures.response import response
from comnsense_agent.automaton.waiting_context import WaitingContext
from comnsense_agent.automaton import State
from comnsense_agent.message import Message
from comnsense_agent.data import Response


def get_context(workbook=None, ready=False):
    context = mock.Mock()
    context.workbook = workbook
    context.is_ready.return_value = ready
    return context


@pytest.yield_fixture(
    params=[random_sheet_change, random_range_response, workbook_open])
def event(request, workbook, sheetname):
    if request.param == workbook_open:
        yield next(workbook_open(workbook))
    else:
        yield next(request.param(workbook, sheetname))


@allure.feature("Automaton")
@allure.story("WaitingContext - WorkbookBeforeClose")
def test_waiting_context_before_close(workbook, before_close):
    context = get_context(workbook)
    msg = Message.event(before_close)
    answer, state = State.WaitingContext.next(context, msg)
    assert_that(answer, is_(none()))
    assert_that(state, is_(none()))


@allure.feature("Automaton")
@allure.story("WaitingContext - Event")
def test_waiting_context_event(workbook, event):
    context = get_context(workbook)
    msg = Message.event(event)
    answer, state = State.WaitingContext.next(context, msg)
    assert_that(answer, is_(none()))
    assert_that(state, State.WaitingContext)


@allure.feature("Automaton")
@allure.story("WaitingContext - Response")
def test_waiting_context_response(workbook, response):
    context = get_context(workbook)
    msg = Message.response(response)
    answer, state = State.WaitingContext.next(context, msg)
    assert_that(answer, is_(none()))
    assert_that(context.loads.mock_calls, equal_to([mock.call(response.data)]))
    assert_that(state, State.WaitingContext)


@allure.feature("Automaton")
@allure.story("WaitingContext - Response - Ready")
def test_waiting_context_response_ready(workbook, response):
    context = get_context(workbook)

    def sideeffect(*args):
        context.is_ready.return_value = True

    context.loads.side_effect = sideeffect

    msg = Message.response(response)
    answer, state = State.WaitingContext.next(context, msg)
    assert_that(answer, is_(none()))
    assert_that(context.loads.mock_calls, equal_to([mock.call(response.data)]))
    assert_that(state, State.Ready)
