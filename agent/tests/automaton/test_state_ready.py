import allure
import pytest
import mock
import collections
from hamcrest import *

from ..fixtures.excel import workbook, sheetname
from ..fixtures.excel import before_close, workbook_open
from ..fixtures.excel import random_sheet_change, random_range_response

from comnsense_agent.automaton.ready import Ready
from comnsense_agent.message import Message
from comnsense_agent.data import Action


def get_context(event=None):
    context = mock.Mock()
    first = mock.Mock()
    first.handle.return_value = [
        Action.request_from_event(event, "$A$1") if event else "first"]
    second = mock.Mock()
    second.handle.return_value = [
        Action.request_from_event(event, "$A$2") if event else "second"]
    context.handlers.return_value = [first, second]
    return context


@allure.feature("Automaton")
@allure.story("Ready - WorkbookBeforeClose")
def test_state_ready_before_close(workbook):
    event = Message.event(next(before_close(workbook)))
    context = get_context()
    node = Ready()
    action, state = node.next(context, event)
    assert_that(action, is_(none()))
    assert_that(state, is_(none()))


@allure.feature("Automaton")
@allure.story("Ready - Ignore Event")
def test_state_ready_ignore(workbook):
    event = Message.event(next(workbook_open(workbook)))
    context = get_context()
    node = Ready()
    action, state = node.next(context, event)
    assert_that(action, is_(none()))
    assert_that(state, equal_to(node))


@allure.feature("Automaton")
@allure.story("Ready")
@pytest.mark.parametrize("event", [random_range_response, random_sheet_change],
                         ids=["RangeResponse", "SheetChange"])
def test_state_ready(workbook, sheetname, event):
    event = next(event(workbook, sheetname))
    context = get_context(event)
    event = Message.event(event)
    node = Ready()
    actions, state = node.next(context, event)
    assert_that(state, equal_to(node))
    assert_that(actions, instance_of(collections.Sequence))
    assert_that(actions, has_length(2))
