import allure
import mock
import os
import pytest
import random
import shutil
import string
import tempfile
import unittest
from hamcrest import *

from comnsense_agent.data import Signal
from comnsense_agent.message import Message
from comnsense_agent.runtime import Runtime
from comnsense_agent.worker import Worker
from comnsense_agent.worker import WorkerProcess
from comnsense_agent.worker import get_worker_command
from comnsense_agent.worker import get_worker_script

from .fixtures.network import port, host
from .fixtures.excel import workbook


def touch(filename):
    with open(filename, 'w'):
        pass


@allure.feature("Worker")
class TestGetWorkerScript(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def test_in_development_mode(self):
        original = os.path.realpath(
            os.path.join(self.tmpdir, "comnsense-worker"))
        touch(original)
        script = get_worker_script(self.tmpdir)
        self.assertEquals(original, script)

    def test_in_py2exe_mode(self):
        original = os.path.realpath(
            os.path.join(self.tmpdir, "comnsense-worker.exe"))
        touch(original)
        script = get_worker_script(self.tmpdir)
        self.assertEquals(original, script)

    def test_not_found(self):
        with pytest.raises(IOError):
            get_worker_script(self.tmpdir)

    def tearDown(self):
        if os.path.isdir(self.tmpdir):
            shutil.rmtree(self.tmpdir)


@allure.feature("Worker")
class TestGetWorkerCommand(unittest.TestCase):
    def setUp(self):
        # TODO replace with get_free_tcp_connection
        port = random.choice(range(30000, 40000))
        self.connection = "tcp://127.0.0.1:%d" % port
        self.ident = "".join(random.sample(string.ascii_letters, 10))
        self.level = random.choice(["DEBUG", "INFO", "ERROR"])

    def basic_test(self, cmd):
        cmd = " ".join(cmd)
        self.assertTrue(cmd.find("-i %s" % self.ident) > 0)
        self.assertTrue(cmd.find("-l %s" % self.level) > 0)
        self.assertTrue(cmd.find("-c %s" % self.connection) > 0)

    def test_in_development_mode(self):
        script = os.path.realpath("comnsense-worker")
        cmd, env = get_worker_command(
            script, self.ident, self.connection, self.level)
        self.assertTrue(cmd[0].lower().find("python") > 0)
        self.assertEquals(cmd[1], script)
        self.basic_test(cmd)

    def test_in_py2exe_mode(self):
        script = os.path.realpath("comnsense-worker.exe")
        cmd, env = get_worker_command(
            script, self.ident, self.connection, self.level)
        self.assertEquals(cmd[0], script)
        self.basic_test(cmd)


@allure.feature("Worker")
class TestWorkerProcess(unittest.TestCase):
    def setUp(self):
        self.proc = mock.Mock()
        self.proc.pid = random.choice(range(1, 65535))

    def test_pid(self):
        wp = WorkerProcess(self.proc)
        self.assertEquals(wp.pid, self.proc.pid)

    def test_is_alive(self):
        wp = WorkerProcess(self.proc)
        self.proc.poll.return_value = None
        self.assertTrue(wp.is_alive())
        self.proc.poll.return_value = 1
        self.assertFalse(wp.is_alive())

    def test_join(self):
        wp = WorkerProcess(self.proc)
        wp.join()
        self.assertEquals(len(self.proc.wait.mock_calls), 1)

    def test_kill(self):
        wp = WorkerProcess(self.proc)
        wp.kill()
        self.assertEquals(len(self.proc.terminate.mock_calls), 1)


@pytest.fixture(scope="module")
def connection(host, port):
    return "tcp://%s:%d" % (host, port)


@pytest.yield_fixture(autouse=True)
def dummy_dealer(monkeypatch):

    from comnsense_agent.socket.zmq_socket import ZMQDealer

    def new(cls, *args, **kwargs):
        dealer = mock.Mock()
        return dealer

    monkeypatch.setattr(ZMQDealer, "__new__", classmethod(new))
    monkeypatch.setattr(ZMQDealer, "__init__", lambda *x, **y: None)

    yield None

    monkeypatch.undo()
    monkeypatch.undo()


@pytest.fixture
def loop():
    return mock.Mock()


@pytest.yield_fixture
def worker(monkeypatch, workbook, connection, loop):
    monkeypatch.setattr("comnsense_agent.worker.worker_logger_setup",
                        lambda *x, **y: None)
    worker = Worker(workbook, connection, loop)
    worker.runtime = mock.Mock()
    yield worker
    monkeypatch.undo()


@allure.feature("Worker")
def test_worker_create_socket(worker, connection, loop):
    assert_that(worker.client.connect.mock_calls,
                equal_to([mock.call(connection, loop)]))
    assert_that(worker.client.on_recv.mock_calls,
                equal_to([mock.call(worker.routine)]))


@allure.feature("Worker")
def test_worker_stop_signal(worker):
    msg = Message.signal(Signal.stop())
    worker.routine(msg)
    assert_that(worker.runtime.run.mock_calls, equal_to([]))
    assert_that(worker.client.send.mock_calls, equal_to([]))
    assert_that(worker.loop.stop.mock_calls, equal_to([mock.call()]))


@allure.feature("Worker")
def test_worker_event(worker):
    msg = Message.event("event")
    worker.runtime.run.return_value = []
    worker.routine(msg)
    assert_that(worker.runtime.run.mock_calls, equal_to([mock.call(msg)]))
    assert_that(worker.client.send.mock_calls, equal_to([]))
    assert_that(worker.loop.stop.mock_calls, equal_to([]))


@allure.feature("Worker")
def test_worker_response(worker):
    msg = Message.response("response")
    worker.runtime.run.return_value = []
    worker.routine(msg)
    assert_that(worker.runtime.run.mock_calls, equal_to([mock.call(msg)]))
    assert_that(worker.client.send.mock_calls, equal_to([]))
    assert_that(worker.loop.stop.mock_calls, equal_to([]))


@allure.feature("Worker")
def test_worker_runtime_finished(worker):
    msg = Message.event("event")
    worker.runtime.run.return_value = Runtime.SpecialAnswer.finished
    worker.routine(msg)
    assert_that(worker.runtime.run.mock_calls, equal_to([mock.call(msg)]))
    assert_that(worker.client.send.mock_calls, equal_to([]))
    assert_that(worker.loop.stop.mock_calls, equal_to([mock.call()]))


@allure.feature("Worker")
def test_worker_runtime_no_answer(worker):
    msg = Message.event("event")
    worker.runtime.run.return_value = Runtime.SpecialAnswer.noanswer
    worker.routine(msg)
    assert_that(worker.runtime.run.mock_calls, equal_to([mock.call(msg)]))
    assert_that(worker.client.send.mock_calls, equal_to([]))
    assert_that(worker.loop.stop.mock_calls, equal_to([]))


@allure.feature("Worker")
def test_worker_runtime_answer(worker):
    event = Message.event("event")
    action = Message.action("action")
    request = Message.request("request")
    worker.runtime.run.return_value = [action, request]
    worker.routine(event)
    assert_that(worker.runtime.run.mock_calls, equal_to([mock.call(event)]))
    assert_that(worker.client.send.mock_calls,
                equal_to([mock.call(action), mock.call(request)]))
    assert_that(worker.loop.stop.mock_calls, equal_to([]))


@allure.feature("Worker")
def test_worker_start(worker):
    worker.start()
    assert_that(worker.client.send.mock_calls,
                equal_to([mock.call(Message.signal(Signal.ready()))]))
    assert_that(worker.loop.start.mock_calls, equal_to([mock.call()]))
    assert_that(worker.client.close.mock_calls, equal_to([mock.call()]))
