import allure
import pytest
import mock
from hamcrest import *

from ..fixtures.excel import before_close, workbook
from comnsense_agent.automaton.waiting_workbook import WaitingWorkbookID
from comnsense_agent.automaton import State
from comnsense_agent.message import Message


def get_context(workbook=None, ready=False):
    context = mock.Mock()
    context.workbook = workbook
    context.is_ready.return_value = False
    return context


@allure.feature("Automaton")
@allure.story("WaitingWorkbookID - WorkbookBeforeClose")
def test_waiting_workbook_before_close(before_close):
    context = get_context()
    msg = Message.event(before_close)
    answer, state = State.WaitingWorkbookID.next(context, msg)
    assert_that(answer, is_(none()))
    assert_that(state, is_(none()))
