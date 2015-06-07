import logging
import time
import sys
import subprocess
import copy
import os

import zmq
from zmq.eventloop import ioloop, zmqstream

from comnsense_agent.message import Message
import comnsense_agent.utils.log as L
from comnsense_agent.data import Signal
from comnsense_agent.runtime import Runtime


class WorkerProcess:
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


def worker_main(ident, connection, loop=None, ctx=None):
    if loop is None:
        loop = ioloop.IOLoop.instance()
    if ctx is None:
        ctx = zmq.Context()

    def setup_socket():
        socket = ctx.socket(zmq.DEALER)
        socket.setsockopt(zmq.IDENTITY, ident)
        socket.connect(connection)
        socket_stream = zmqstream.ZMQStream(socket, loop)
        return socket_stream

    def setup_logger(socket):
        L.worker_setup(socket, ident)
        return logging.getLogger(__name__)

    socket_stream = setup_socket()
    logger = setup_logger(socket_stream)
    runtime = Runtime()

    def on_signal_recv(msg):
        signal = Signal.deserialize(msg.payload)
        if signal.code == Signal.Code.Stop.value:
            loop.stop()
        else:
            logger.warn("unexpected signal: %s", signal)

    def on_recv(msg):
        logger.debug("worker on_recv: %s", msg)
        if msg.is_signal():
            on_signal_recv(msg)
        if msg.is_request():
            socket_stream.send_multipart(list(msg))
        elif msg.is_event() or msg.is_response():
            answer = runtime.run(msg)
            if isinstance(answer, tuple):
                for a in answer:
                    socket_stream.send_multipart(list(a))
            elif answer is not None:
                socket_stream.send_multipart(list(answer))
        else:
            logger.warn("unexpected message kind: %s", msg.kind)

    socket_stream.on_recv(Message.call(on_recv))

    # TODO fix it, strange
    socket_stream.send_multipart(
        list(Message.signal(Signal.ready())))

    loop.start()


def run_worker(ident, connection):
    logger = logging.getLogger(__name__)
    env = copy.deepcopy(os.environ)
    start_script = os.path.realpath(
        os.path.join(os.path.dirname(sys.argv[0]), "comnsense-worker"))
    if not os.path.exists(start_script):
        if os.path.exists(start_script + ".exe"):
            start_script = start_script + ".exe"
        else:
            raise IOError("%s: no such file or directory" % start_script)
    
    cmd = [start_script, '-i', ident, '-c', connection]
    if not start_script.endswith(".exe"):
        cmd.insert(0, sys.executable)
        env['PYTHONPATH'] = os.path.join(os.path.dirname(__file__), "..")
    logger.debug("worker cmd: %s", cmd)
    proc = subprocess.Popen(cmd, close_fds=True, env=env)
    logger.info("worker for ident %s was started: %s", ident, proc.pid)
    return WorkerProcess(proc)
