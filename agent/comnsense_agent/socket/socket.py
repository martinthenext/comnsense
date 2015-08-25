import logging


logger = logging.getLogger(__name__)


class Socket(object):
    """
    `Socket` is abstract class that defines common interface for sockets.
    """

    def bind(self, address, loop):
        """
        Binds socket with specific *address* and *loop*.

        :param address: some address string, e.g: ``tcp://127.0.0.1:80``
        :type address:  str

        :param loop:    event loop in which socket should be registered
        :type loop:     `IOLoop <ioloop_>`_
        """
        raise NotImplementedError("abstract method was called")

    def connect(self, address, loop):
        """
        Connects socket to existing listener

        :param address: some address string, e.g: ``tcp://127.0.0.1:80``
        :type address:  str

        :param loop:    event loop in which socket should be registered
        :type loop:     `IOLoop <ioloop_>`_
        """
        raise NotImplementedError("abstract method was called")

    def send(self, message):
        """
        Send *message* via socket.

        :param message: is data that should be sent
        :type message:  `Message`
        """
        raise NotImplementedError("abstract method was called")

    def on_recv(self, callback):
        """
        Regist *callback* that will be called
        for each received `Message <message>`.

        *callback* is callable object with one argument `Message <message>`.
        """
        raise NotImplementedError("abstract method was called")

    def on_send(self, callback):
        """
        Regist *callback* that will be called
        for each sent `Message <message>`.

        *callback* is callable object with one argument `Message <message>`.
        """
        raise NotImplementedError("abstract method was called")

    def close(self):
        """
        Drops connection and releases related resources.
        """
        raise NotImplementedError("abstract method was called")


class SocketError(RuntimeError):
    """
    `Socket` specific exception.

    If *code* if not defined ``SOCK000`` is used.
    """
    def __init__(self, message, code=None):
        if code is None:
            code = "SOCK000"
        super(SocketError, self).__init__("[%s] %s" % (code, message))


class AddressAlreadyInUse(SocketError):
    """
    Raises when socket tryes to bind existing address.

    Code ``SOCK001``.
    """
    def __init__(self, addr):
        super(AddressAlreadyInUse, self).__init__(
            "'%s' already in use" % addr, "SOCK001")


class NoAvailablePorts(SocketError):
    """
    Raises when socket could not find free port to bind.

    Code ``SOCK002``
    """
    def __init__(self, port_range):
        super(NoAvailablePorts, self).__init__(
            "there are no available ports in range %s" % port_range, "SOCK002")
