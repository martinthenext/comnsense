import logging
import random
import pickle
import sys
import time

# import zmq
# from zmq.eventloop import ioloop, zmqstream

from comnsense_agent.serverstream import ServerStream
from comnsense_agent.worker import create_new_worker
from comnsense_agent.message import Message
from comnsense_agent.data import Signal
from comnsense_agent.socket import ZMQRouter, ZMQDealer


logger = logging.getLogger(__name__)


class Agent:
    def __init__(self, bind_str, server_str):
        self.bind_str = bind_str
        self.server_str = server_str
        logger.debug("server connection str: %s", server_str)

    def create_frontend_socket(self, loop):
        frontend = ZMQRouter()
        frontend.bind(self.bind_str, loop)
        logger.info("frontend socket bind: %s", self.bind_str)
        return frontend

    def setup_server(self, loop):
        server_stream = ServerStream(self.server_str, loop)
        return server_stream

    def create_backend_socket(self, loop):
        backend = ZMQRouter()
        bind_str = backend.bind_unused_port(loop)
        logger.debug("backend socket bind: %s", bind_str)
        return backend, bind_str

    def run(self, loop=None):
        if loop is None:
            loop = ioloop.IOLoop.instance()

        server_stream = self.setup_server(loop)
        frontend = self.create_frontend_socket(loop)
        backend, backend_conn = self.create_backend_socket(loop)

        workers = {}

        def on_frontend_recv(msg):
            logger.debug("frontend recv: %s", msg)
            if msg.is_event() or msg.is_request() or msg.is_signal():
                if msg.ident not in workers or \
                        not workers[msg.ident].is_alive():
                    worker = create_new_worker(msg.ident, backend_conn)
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
                    backend.send(msg)
            else:
                logger.warn("unexpected message kind: %s", msg.kind)

        def on_backend_recv(msg):  # receive answer from backend
            if msg.is_action():
                logger.debug("send to excel: %s", msg)
                frontend.send(msg)  # send answer to excel
            elif msg.is_request():  # send request to server
                server_stream.send(msg)
            elif msg.is_log():  # log from backend
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
            backend.send(msg)

        frontend.on_recv(on_frontend_recv)
        backend.on_recv(on_backend_recv)
        server_stream.on_recv(on_server_recv)
        try:
            loop.start()
        finally:
            for worker in workers.values():
                if worker.is_alive():
                    worker.kill()
                    worker.join()

            frontend.close()
            backend.close()
