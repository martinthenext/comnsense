import logging
import random
import pickle
import time

from comnsense_agent.serverstream import ServerStream
from comnsense_agent.worker import create_new_worker
from comnsense_agent.message import Message
from comnsense_agent.data import Signal
from comnsense_agent.socket import ZMQRouter, ZMQDealer


logger = logging.getLogger(__name__)


class Agent(object):
    def __init__(self, frontend_bind, server_address, loop):
        self.frontend, _ = Agent.create_frontend_socket(loop, frontend_bind)
        self.backend, self.backend_bind = Agent.create_backend_socket(loop)
        self.client, _ = Agent.create_client_socket(loop, server_address)

        self.frontend.on_recv(self.frontend_routine)
        self.backend.on_recv(self.backend_routine)
        self.client.on_recv(self.client_routine)

        self.workers = {}
        self.loop = loop

    @staticmethod
    def create_frontend_socket(loop, bind_str):
        frontend = ZMQRouter()
        frontend.bind(bind_str, loop)
        logger.info("frontend socket bind: %s", bind_str)
        return frontend, bind_str

    @staticmethod
    def create_client_socket(loop, address):
        client = ServerStream(address, loop)
        logger.info("client connects to: %s", address)
        return client, address

    @staticmethod
    def create_backend_socket(loop):
        backend = ZMQRouter()
        bind_str = backend.bind_unused_port(loop)
        logger.info("backend socket bind: %s", bind_str)
        return backend, bind_str

    def frontend_routine(self, msg):
        if msg.is_event():
            logger.debug("receive from addin: %s", msg)

            if msg.ident not in self.workers or \
                    not self.workers[msg.ident].is_alive():
                worker = create_new_worker(msg.ident, self.backend_bind)
                self.workers[msg.ident] = worker
                # TODO redo this
                time.sleep(3)

            self.backend.send(msg)

    def backend_routine(self, msg):
        if msg.is_action():
            logger.debug("send to addin: %s", msg)
            self.frontend.send(msg)

        elif msg.is_request():
            self.client.send(msg)

        elif msg.is_log():
            logger.handle(pickle.loads(msg.payload))

        elif msg.is_signal():
            signal = Signal.deserialize(msg.payload)
            if signal.code == Signal.Code.Ready:
                logger.info("worker with ident %s is ready", msg.ident)

    def client_routine(self, msg):
        if msg.is_response():
            self.backend.send(msg)

    def start(self):
        try:
            self.loop.start()
        finally:
            for worker in self.workers.values():
                if worker.is_alive():
                    worker.kill()
                    worker.join()

            self.frontend.close()
            self.backend.close()
