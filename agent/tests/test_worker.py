import mock
import os
import pytest
import random
import shutil
import string
import tempfile
import unittest

from comnsense_agent.worker import get_worker_script
from comnsense_agent.worker import get_worker_command
from comnsense_agent.worker import WorkerProcess


def touch(filename):
    with open(filename, 'w'):
        pass


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
