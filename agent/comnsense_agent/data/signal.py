import logging
import msgpack

logger = logging.getLogger(__name__)

SIGNAL_STOP = 0
SIGNAL_READY = 1

SIGNALS = [
    SIGNAL_STOP,
    SIGNAL_READY
]


class SignalError(RuntimeError):
    pass


class Signal:
    """
    Signals should be used for service messages in interservice communication.
    It shall not contain the data if possible.
    """
    __slots__ = ("code", "data")

    def __init__(self, code, data=None):
        self.code = code
        self.data = data
        if self.code not in SIGNALS:
            raise SignalError("unknown signal code: %s", code)

    @staticmethod
    def deserialize(data):
        """
        Creates :py:class:`Signal` from byte string representation

        :param str data: Byte string representation
        :return: :py:class:`Signal` object
        """
        return Signal(*msgpack.unpackb(data, encoding='utf-8'))

    def serialize(self):
        """
        Make byte string representation of signal

        :return: byte string
        """
        return msgpack.packb([self.code, self.data], use_bin_type=True)

    def __str__(self):
        if self.data is None:
            return "Signal {code:%d}" % self.code
        return "Signal {code:%d, data:%s}" % (self.code, self.data)

    @staticmethod
    def ready(identity=None):
        """
        Signal READY.
        It should be used to notify agent about readiness of service.

        :param identity:  optional service identity.
        :type identity: str or None

        :return: :py:class:`Signal`
        """
        return Signal(SIGNAL_READY, identity)

    @staticmethod
    def stop():
        """
        Signal STOP.
        Agent should send this signal to service to stop it.

        :return: :py:class:`Signal`
        """
        return Signal(SIGNAL_STOP)

    def __eq__(self, sig):
        return isinstance(sig, Signal) and \
                self.code == sig.code and \
                self.data == sig.data

    def __ne__(self, sig):
        return not self.__eq__(sig)
