import logging
import sys
import random

import zmq
from zmq.eventloop import zmqstream

from comnsense_agent.message import Message

from .socket import Socket
from .socket import NoAvailablePorts, AddressAlreadyInUse, SocketError

logger = logging.getLogger(__name__)


class ZMQSocket(Socket):
    LINGER = 1000
    IO_THREADS = 1

    def __init__(self, kind, context=None):
        context = context or zmq.Context.instance(ZMQSocket.IO_THREADS)
        self._socket = context.socket(kind)

    def bind(self, address, loop):
        try:
            self._socket.bind(address)
        except zmq.error.ZMQError, e:
            if e.errno == 48:
                raise AddressAlreadyInUse(address)
            else:
                raise SocketError(e.msg)
        self._stream = zmqstream.ZMQStream(self._socket, loop)

    def connect(self, address, loop):
        self._socket.connect(address)
        self._stream = zmqstream.ZMQStream(self._socket, loop)

    def send(self, message):
        if not self._stream.closed():
            self._stream.send_multipart(list(message))

    def on_recv(self, callback):
        def oncall(data):
            try:
                msg = Message(*data)
                return callback(msg)
            except:
                etype, evalue, etb = sys.exc_info()
                logger.exception(evalue)

        self._stream.on_recv(oncall)

    def on_send(self, callback):
        def oncall(data, status=None):
            try:
                msg = Message(*data)
                return callback(msg)
            except:
                etype, evalue, etb = sys.exc_info()
                logger.exception(evalue)

        self._stream.on_send(oncall)

    def close(self):
        if not self._stream.closed():
            self._stream.close(ZMQSocket.LINGER)


class ZMQRouter(ZMQSocket):
    MIN_PORT = 30000
    MAX_PORT = 50000

    def __init__(self):
        super(ZMQRouter, self).__init__(zmq.ROUTER)

    def bind_unused_port(self, loop, host="127.0.0.1", port_range=None):
        if port_range is None:
            port_range = (ZMQRouter.MIN_PORT, ZMQRouter.MAX_PORT)

        ports = range(*port_range)
        random.shuffle(ports)

        for port in ports:
            address = "tcp://%s:%d" % (host, port)
            try:
                self._socket.bind(address)
            except zmq.error.ZMQError, e:
                if e.errno == 48:
                    continue
                else:
                    raise
            else:
                self._stream = zmqstream.ZMQStream(self._socket, loop)
                return address

        raise NoAvailablePorts(port_range)


class ZMQDealer(ZMQSocket):
    def __init__(self, identity=None):
        super(ZMQDealer, self).__init__(zmq.DEALER)
        if identity is not None:
            self._socket.setsockopt(zmq.IDENTITY, identity)
