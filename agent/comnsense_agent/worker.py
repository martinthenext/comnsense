import copy
import logging
import os
import subprocess
import sys

from comnsense_agent.data import Signal
from comnsense_agent.message import Message
from comnsense_agent.runtime import Runtime
from comnsense_agent.socket import ZMQDealer
from comnsense_agent.utils.log import worker_setup as worker_logger_setup


class Worker(object):
    def __init__(self, session, address, loop):
        self.loop = loop

        self.client = self.create_client_socket(session, address, loop)
        self.client.on_recv(self.routine)
        self.setup_logger(session)

        self.runtime = Runtime()

    def create_client_socket(self, session, address, loop):
        socket = ZMQDealer(session)
        socket.connect(address, loop)
        return socket

    def setup_logger(self, session):
        global logger
        worker_logger_setup(self.client, session)
        logger = logging.getLogger(__name__)

    def routine(self, msg):
        if msg.is_signal():
            signal = Signal.deserialize(msg.payload)
            if signal.code == Signal.Code.Stop:
                self.loop.stop()

        elif msg.is_event() or msg.is_response():
            answer = self.runtime.run(msg)
            logger.debug("runtime answer: %s", repr(answer))

            if answer == Runtime.SpecialAnswer.finished:
                self.loop.stop()
            elif answer != Runtime.SpecialAnswer.noanswer:
                for msg in answer:
                    self.client.send(msg)

    def start(self):
        self.client.send(Message.signal(Signal.ready()))
        try:
            self.loop.start()
        finally:
            self.client.close()


class WorkerProcess(object):
    __slots__ = ("popen",)

    def __init__(self, popen):
        self.popen = popen

    def is_alive(self):
        return self.popen.poll() is None

    def join(self):
        return self.popen.wait()

    def kill(self):
        return self.popen.terminate()

    pid = property(lambda x: x.popen.pid)


def get_worker_script(searchpath=None):
    if searchpath is None:
        searchpath = os.path.dirname(sys.argv[0])
    script = os.path.realpath(
        os.path.join(searchpath, "comnsense-worker"))
    if not os.path.exists(script):
        if os.path.exists(script + ".exe"):  # py2exe?
            script = script + ".exe"
        else:
            raise IOError("%s: no such file or directory" % script)
    return script


def get_worker_command(script, ident, connection, level="DEBUG"):
    env = copy.deepcopy(os.environ)
    cmd = [script, '-i', ident, '-c', connection, '-l', level]
    if not script.endswith(".exe"):  # development mode
        cmd.insert(0, sys.executable)
        env['PYTHONPATH'] = os.path.realpath(
            os.path.join(os.path.dirname(__file__), ".."))
    return cmd, env


def create_new_worker(ident, connection):
    logger = logging.getLogger(__name__)
    script = get_worker_script()
    cmd, env = get_worker_command(script, ident, connection)
    logger.debug("worker env: %s", repr(env))
    logger.debug("worker cmd: %s", cmd)
    proc = subprocess.Popen(cmd, close_fds=True, env=env)
    logger.info("worker for ident %s was started: %s", ident, proc.pid)
    return WorkerProcess(proc)
