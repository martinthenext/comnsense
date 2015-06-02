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
    __slots__ = ("code", "data")

    def __init__(self, code, data=None):
        self.code = code
        self.data = data
        if self.code not in SIGNALS:
            raise SignalError("unknown signal code: %s", code)

    @staticmethod
    def deserialize(data):
        return Signal(*msgpack.unpackb(data, encoding='utf-8'))

    def serialize(self):
        return msgpack.packb([self.code, self.data], use_bin_type=True)

    def __str__(self):
        if self.data is None:
            return "Signal {code:%d}" % self.code
        return "Signal {code:%d, data:%s}" % (self.code, self.data)

    @staticmethod
    def ready(identity=None):
        return Signal(SIGNAL_READY, identity)

    @staticmethod
    def stop():
        return Signal(SIGNAL_STOP)

    def __eq__(self, sig):
        return isinstance(sig, Signal) and \
                self.code == sig.code and \
                self.data == sig.data

    def __ne__(self, sig):
        return not self.__eq__(sig)
