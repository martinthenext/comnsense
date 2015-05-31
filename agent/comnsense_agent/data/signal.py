import logging
import pickle

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
        return Signal(*pickle.loads(data))

    def serialize(self):
        return pickle.dumps([self.code, self.data])

    def __str__(self):
        if self.data is None:
            return "Signal {code:%d}" % self.code
        return "Signal {code:%d, data:%s}" % (self.code, self.data)

    @staticmethod
    def ready():
        return Signal(SIGNAL_READY)

    @staticmethod
    def stop():
        return Signal(SIGNAL_STOP)
