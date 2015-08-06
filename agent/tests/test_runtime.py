import pytest
import allure
from hamcrest import *

from comnsense_agent.runtime import Runtime
from comnsense_agent.message import Message

MESSAGE = Message.action("something")
FIXTURES = [
    (None, Runtime.SpecialAnswer.noanswer),
    ([], []),
    (MESSAGE, [MESSAGE]),
    ([MESSAGE], [MESSAGE]),
    ([MESSAGE, MESSAGE], [MESSAGE, MESSAGE]),
    ([MESSAGE, None], [MESSAGE]),
    (["something"], []),
    ("something", [])]


@allure.feature("Automaton")
@allure.story("Runtime - Prepare Answer")
@pytest.mark.parametrize("answer, expected", FIXTURES)
def test_runtime_prepare_answer(answer, expected):
    runtime = Runtime()
    prepared = runtime.prepare_answer(answer)
    assert_that(prepared, equal_to(expected))


@allure.feature("Automaton")
@allure.story("Runtime - Prepare Answer - No State")
@pytest.mark.parametrize("answer, _", FIXTURES)
def test_runtime_prepare_answer_finished(answer, _):
    runtime = Runtime()
    runtime.currentState = None
    prepared = runtime.prepare_answer(answer)
    assert_that(prepared, equal_to(Runtime.SpecialAnswer.finished))
