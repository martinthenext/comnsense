import allure
import pytest
import mock
from hamcrest import *

from ..fixtures.excel import before_close, workbook, sheetname
from ..fixtures.excel import random_range_response, random_sheet_change
from ..fixtures.excel import workbook_open
from comnsense_agent.automaton.waiting_workbook import WaitingWorkbookID
from comnsense_agent.automaton import State
from comnsense_agent.message import Message
from comnsense_agent.data import Request


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
@allure.story("WaitingWorkbookID - WorkbookBeforeClose")
def test_waiting_workbook_before_close(before_close):
    context = get_context()
    msg = Message.event(before_close)
    answer, state = State.WaitingWorkbookID.next(context, msg)
    assert_that(answer, is_(none()))
    assert_that(state, is_(none()))


@allure.feature("Automaton")
@allure.story("WaitingWorkbookID - Event - Waiting")
def test_waiting_workbook_event(event):
    context = get_context()
    msg = Message.event(event)
    answer, state = State.WaitingWorkbookID.next(context, msg)
    assert_that(context.workbook, event.workbook)
    assert_that(answer, instance_of(Message))
    assert_that(answer.is_request())
    request = Request.deserialize(answer.payload)
    assert_that(request.type, is_(Request.Type.GetContext))
    assert_that(state, is_(State.WaitingContext))


@allure.feature("Automaton")
@allure.story("WaitingWorkbookID - Event - Ready")
def test_waiting_workbook_event_ready(event):
    context = get_context(event.workbook, True)
    msg = Message.event(event)
    answer, state = State.WaitingWorkbookID.next(context, msg)
    assert_that(context.workbook, event.workbook)
    assert_that(answer, is_(none()))
    assert_that(state, is_(State.Ready))
