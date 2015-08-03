import pytest
import unittest
import allure
import random
import string


from comnsense_agent.runtime import Runtime
from comnsense_agent.message import Message, MESSAGE_RESPONSE
from comnsense_agent.data import Event
from comnsense_agent.data import Request
from comnsense_agent.data import Response
from comnsense_agent.data import Signal

from .common import COMNSENSE_WIKI


@pytest.mark.skipif(True, reason="It is needed to reafctoring")
@allure.testcase(COMNSENSE_WIKI + '/Runtime-test:-Initialization')
class TestRuntimeInitialization(unittest.TestCase):
    @pytest.allure.step("creating new runtime")
    def get_new_runtime(self):
        runtime = Runtime()
        return runtime

    @pytest.allure.step("creating valid event message")
    def get_valid_event_message(self, workbook):
        msg = Message.event(Event(Event.Type.WorkbookOpen,
                                  workbook, None, None))
        return msg

    @pytest.allure.step("creating valid response message")
    def get_valid_response_message(self, workbook):
        # TODO make sensible response
        return Message.response(Response(200, {"key": "value"}))

    @pytest.allure.step("creating valid signal message")
    def get_valid_signal_message(self, workbook):
        return Message.signal(Signal.ready(workbook))

    @pytest.allure.step("creating invalid message with kind: {1}")
    def get_invalid_message(self, kind):
        return Message(kind, "".join(random.sample(string.ascii_letters, 10)))

    @pytest.allure.step("executing runtime")
    def execute_runtime(self, runtime, msg):
        return runtime.run(msg)

    @pytest.allure.step("check state - initial")
    def check_state_initial(self, runtime):
        self.assertFalse(runtime.context.is_ready())
        self.assertTrue(runtime.context.workbook is None)

    @pytest.allure.step("check state - waiting context")
    def check_state_waiting_context(self, runtime, msg, workbook):
        self.assertFalse(msg is None)
        self.assertFalse(isinstance(msg, tuple))
        self.assertTrue(msg.is_request())
        request = Request.deserialize(msg.payload)
        self.assertEquals(request.type, Request.Type.GetContext)
        self.assertEquals(request.data, {"workbook": workbook})
        self.assertFalse(runtime.context.is_ready())
        self.assertEquals(runtime.context.workbook, workbook)

    @pytest.allure.step("check state - ready")
    def check_state_ready(self, runtime, msg):
        self.assertTrue(msg is None)
        self.assertTrue(runtime.context.is_ready())

    def test_event(self):
        workbook = "".join(random.sample(string.ascii_letters, 10))
        runtime = self.get_new_runtime()
        self.check_state_initial(runtime)
        event_msg = self.get_valid_event_message(workbook)
        request_msg = self.execute_runtime(runtime, event_msg)
        self.check_state_waiting_context(runtime, request_msg, workbook)
        response_msg = self.get_valid_response_message(workbook)
        answer = self.execute_runtime(runtime, response_msg)
        self.check_state_ready(runtime, answer)

    def test_signal(self):
        workbook = "".join(random.sample(string.ascii_letters, 10))
        runtime = self.get_new_runtime()
        self.check_state_initial(runtime)
        signal_msg = self.get_valid_signal_message(workbook)
        request_msg = self.execute_runtime(runtime, signal_msg)
        self.check_state_waiting_context(runtime, request_msg, workbook)
        response_msg = self.get_valid_response_message(workbook)
        answer = self.execute_runtime(runtime, response_msg)
        self.check_state_ready(runtime, answer)

    def test_wrong_first_message(self):
        runtime = self.get_new_runtime()
        self.check_state_initial(runtime)
        msg = self.get_invalid_message(MESSAGE_RESPONSE)
        answer = self.execute_runtime(runtime, msg)
        self.check_state_initial(runtime)
