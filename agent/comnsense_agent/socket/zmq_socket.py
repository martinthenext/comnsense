import logging
import sys

import zmq
from zmq.eventloop import zmqstream

from .socket import Socket, AddressAlreadyInUse, SocketError
from comnsense_agent.message import Message

logger = logging.getLogger(__name__)


class ZMQContext(object):
    __context = None

    def __new__(cls, *args, **kwargs):
        if ZMQContext.__context is None:
            ZMQContext.__context = object.__new__(cls, *args, **kwargs)
        return ZMQContext.__context

    def __init__(self):
        self._context = zmq.Context()
        self._sock_count = 0

    @property
    def instance(self):
        return self._context

    def create_socket(self, kind):
        sock = self._context.socket(kind)
        self._sock_count += 1
        return sock

    def release_socket(self):
        self._sock_count -= 1
        if self._sock_count == 0:
            self.destroy()

    def destroy(self):
        self._context.destroy()
        self._context.term()
        ZMQContext.__context = None

    def __del__(self):
        self.destroy()


class ZMQSocket(Socket):
    LINGER = 1000

    def __init__(self, kind):
        self._socket = ZMQContext().create_socket(kind)

    def bind(self, address, loop):
        try:
            self._socket.bind(address)
        except zmq.error.ZMQError, e:
            if e.errno == 48:
                raise AddressAlreadyInUse(address)
            else:
                raise SocketError(e.msg)
        self._stream = zmqstream.ZMQStream(self._socket, loop)
        self._stream.set_close_callback(ZMQContext().release_socket)

    def connect(self, address, loop):
        self._socket.connect(address)
        self._stream = zmqstream.ZMQStream(self._socket, loop)
        self._stream.set_close_callback(ZMQContext().release_socket)

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
    def __init__(self):
        super(ZMQRouter, self).__init__(zmq.ROUTER)


class ZMQDealer(ZMQSocket):
    def __init__(self):
        super(ZMQDealer, self).__init__(zmq.DEALER)
