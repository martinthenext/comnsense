import logging


logger = logging.getLogger(__name__)


class Socket(object):
    def bind(self, address, loop):
        raise NotImplementedError("abstract method was called")

    def connect(self, address, loop):
        raise NotImplementedError("abstract method was called")

    def send(self, message):
        raise NotImplementedError("abstract method was called")

    def on_recv(self, callback):
        raise NotImplementedError("abstract method was called")

    def close(self):
        raise NotImplementedError("abstract method was called")


class SocketError(RuntimeError):
    def __init__(self, message, code=None):
        if code is None:
            code = "SOCK000"
        super(SocketError, self).__init__("[%s] %s" % (code, message))


class AddressAlreadyInUse(SocketError):
    def __init__(self, addr):
        super(AddressAlreadyInUse, self).__init__(
            "'%s' already in use" % addr, "SOCK001")


class NoAvailablePorts(SocketError):
    def __init__(self, port_range):
        super(NoAvailablePorts, self).__init__(
            "there are no available ports in range %s" % port_range, "SOCK002")
