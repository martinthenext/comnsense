import logging
import random
import pickle
import sys
import time

import zmq
from zmq.eventloop import ioloop, zmqstream

from comnsense_agent.serverstream import ServerStream
from comnsense_agent.worker import create_new_worker
from comnsense_agent.message import Message
from comnsense_agent.data import Signal


logger = logging.getLogger(__name__)


class Agent:
    def __init__(self, bind_str, server_str):
        self.context = zmq.Context()
        self.bind_str = bind_str
        logger.debug("bind socket: %s", bind_str)
        self.server_str = server_str
        logger.debug("server connection str: %s", server_str)
        self.port_range = (30000, 40000)
        logger.debug("iam: %s", sys.argv)

    def setup_agent(self, ctx, loop):
        logger.debug("setup agent socket")
        agent = ctx.socket(zmq.ROUTER)
        agent.bind(self.bind_str)

        def on_close(*args):
            logger.warn("agent stream is closed: %s", args)

        agent_stream = zmqstream.ZMQStream(agent, loop)
        agent_stream.set_close_callback(on_close)
        return agent_stream

    def setup_server(self, ctx, loop):
        logger.debug("setup server socket")
        if self.server_str.startswith("https://") or \
                self.server_str.startswith("http://"):
            server_stream = ServerStream(self.server_str, loop)
            return server_stream
        else:
            server = ctx.socket(zmq.DEALER)
            server.connect(self.server_str)
            server_stream = zmqstream.ZMQStream(server, loop)
            return server_stream

    def setup_worker(self, ctx, loop):
        logger.debug("setup worker socket")
        worker = ctx.socket(zmq.ROUTER)
        port_range = range(*self.port_range)
        random.shuffle(port_range)
        conn_str = ""
        for port in port_range:
            try:
                logger.debug("try port %d", port)
                conn_str = "tcp://127.0.0.1:%d" % port
                worker.bind(conn_str)
            except zmq.error.ZMQError, e:
                if e.errno != 48:  # address already in use
                    raise
            else:
                break
        logger.debug("worker bind str: %s", conn_str)

        def on_close(*args):
            logger.warn("worker stream is closed: %s", args)

        worker_stream = zmqstream.ZMQStream(worker, loop)
        worker_stream.set_close_callback(on_close)
        return worker_stream, conn_str

    def run(self, loop=None, ctx=None):
        if loop is None:
            loop = ioloop.IOLoop.instance()
        if ctx is None:
            ctx = zmq.Context()

        server_stream = self.setup_server(ctx, loop)
        agent_stream = self.setup_agent(ctx, loop)
        worker_stream, worker_conn = self.setup_worker(ctx, loop)

        workers = {}

        def on_agent_recv(msg):
            logger.debug("on_agent_recv: %s", msg)
            if msg.is_event() or msg.is_request() or msg.is_signal():
                if msg.ident not in workers or \
                        not workers[msg.ident].is_alive():
                    worker = create_new_worker(msg.ident, worker_conn)
                    workers[msg.ident] = worker
                    # TODO redo this
                    time.sleep(3)
                if msg.is_signal():
                    signal = Signal.deserialize(msg.payload)
                    if signal.code == Signal.Code.Ready:
                        logger.info("workbook %s is ready", msg.ident)
                    else:
                        logger.warn("unexpected signal: %s", signal)
                else:
                    worker_stream.send_multipart(list(msg))
            else:
                logger.warn("unexpected message kind: %s", msg.kind)

        def on_worker_recv(msg):  # receive answer from worker
            if msg.is_action():
                agent_stream.send_multipart(list(msg))  # send answer to excel
                logger.debug("send to excel: %s", msg)
            elif msg.is_request():  # send request to server
                server_stream.send_multipart(list(msg))
            elif msg.is_log():  # log from worker
                logger.handle(pickle.loads(msg.payload))
            elif msg.is_signal():
                signal = Signal.deserialize(msg.payload)
                if signal.code == Signal.Code.Ready:
                    logger.info("worker with ident %s is ready", msg.ident)
                else:
                    logger.warn("unexpected signal: %s", signal)
            else:
                logger.warn("unexpected message kind: %s", msg.kind)

        def on_server_recv(msg):
            worker_stream.send_multipart(msg)

        agent_stream.on_recv(Message.call(on_agent_recv))
        worker_stream.on_recv(Message.call(on_worker_recv))
        server_stream.on_recv(Message.call(on_server_recv))
        try:
            loop.start()
        finally:
            for worker in workers.values():
                if worker.is_alive():
                    worker.kill()
                    worker.join()
