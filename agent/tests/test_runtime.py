import pytest
import unittest
import allure
import random
import string


from comnsense_agent.runtime import Runtime
from comnsense_agent.message import KIND_EVENT, KIND_REQUEST, KIND_RESPONSE
from comnsense_agent.message import KIND_SIGNAL, KINDS
from comnsense_agent.message import Message
from comnsense_agent.data import Event, EVENT_WORKBOOK_OPEN
from comnsense_agent.data import Request, REQUEST_GETMODEL
from comnsense_agent.data import Response
from comnsense_agent.data import Signal


@allure.testcase('https://github.com/martinthenext/comnsense/wiki/Runtime-test:-Initialization')
class TestRuntimeInitialization(unittest.TestCase):
    @pytest.allure.step("creating new runtime")
    def get_new_runtime(self):
        runtime = Runtime()
        return runtime

    @pytest.allure.step("creating valid event message")
    def get_valid_event_message(self, workbook):
        msg = Message(
            KIND_EVENT, Event(EVENT_WORKBOOK_OPEN, workbook, None, None))
        return msg

    @pytest.allure.step("creating valid response message")
    def get_valid_response_message(self, workbook):
        # TODO make sensible response
        return Message(KIND_RESPONSE, Response(200, {"key": "value"}))

    @pytest.allure.step("creating valid signal message")
    def get_valid_signal_message(self, workbook):
        return Message(KIND_SIGNAL, Signal.ready(workbook))

    @pytest.allure.step("creating invalid message with kind: {1}")
    def get_invalid_message(self, kind):
        return Message(kind, "".join(random.sample(string.ascii_letters, 10)))

    @pytest.allure.step("executing runtime")
    def execute_runtime(self, runtime, msg):
        return runtime.run(msg)

    @pytest.allure.step("check state - initial")
    def check_state_initial(self, runtime):
        self.assertFalse(runtime.model.is_ready())
        self.assertTrue(runtime.model.workbook is None)

    @pytest.allure.step("check state - waiting model")
    def check_state_waiting_model(self, runtime, msg, workbook):
        self.assertFalse(msg is None)
        self.assertFalse(isinstance(msg, tuple))
        self.assertEquals(msg.kind, KIND_REQUEST)
        request = Request.deserialize(msg.payload)
        self.assertEquals(request.type, REQUEST_GETMODEL)
        self.assertEquals(request.data, {"workbook": workbook})
        self.assertFalse(runtime.model.is_ready())
        self.assertEquals(runtime.model.workbook, workbook)

    @pytest.allure.step("check state - ready")
    def check_state_ready(self, runtime, msg):
        self.assertTrue(msg is None)
        self.assertTrue(runtime.model.is_ready())

    def test_event(self):
        workbook = "".join(random.sample(string.ascii_letters, 10))
        runtime = self.get_new_runtime()
        self.check_state_initial(runtime)
        event_msg = self.get_valid_event_message(workbook)
        request_msg = self.execute_runtime(runtime, event_msg)
        self.check_state_waiting_model(runtime, request_msg, workbook)
        response_msg = self.get_valid_response_message(workbook)
        answer = self.execute_runtime(runtime, response_msg)
        self.check_state_ready(runtime, answer)

    def test_signal(self):
        workbook = "".join(random.sample(string.ascii_letters, 10))
        runtime = self.get_new_runtime()
        self.check_state_initial(runtime)
        signal_msg = self.get_valid_signal_message(workbook)
        request_msg = self.execute_runtime(runtime, signal_msg)
        self.check_state_waiting_model(runtime, request_msg, workbook)
        response_msg = self.get_valid_response_message(workbook)
        answer = self.execute_runtime(runtime, response_msg)
        self.check_state_ready(runtime, answer)

    def test_wrong_first_message(self):
        runtime = self.get_new_runtime()
        self.check_state_initial(runtime)
        msg = self.get_invalid_message(KIND_RESPONSE)
        answer = self.execute_runtime(runtime, msg)
        self.check_state_initial(runtime)
