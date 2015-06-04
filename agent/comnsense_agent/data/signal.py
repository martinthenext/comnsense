import logging
import msgpack
import enum

logger = logging.getLogger(__name__)


class SignalError(RuntimeError):
    pass


class Signal:
    """
    Signals should be used for service messages in interservice communication.
    It shall not contain the data if possible.
    """

    @enum.unique
    class Code(enum.IntEnum):
        """
        Signal code enumeration

        .. py:attribute:: Stop

           Stop signal code

        .. py:attribute:: Ready

           Ready signal code
        """
        Stop = 0
        Ready = 1

    __slots__ = ("code", "data")

    def __init__(self, code, data=None):
        self.code = code
        self.data = data
        if not isinstance(code, Signal.Code):
            raise SignalError("code should be member of Signal.Code")

    @staticmethod
    def deserialize(data):
        """
        Creates :py:class:`Signal` from byte string representation

        :param str data: Byte string representation
        :return: :py:class:`Signal` object
        """
        code, data = msgpack.unpackb(data, encoding='utf-8')
        return Signal(Signal.Code(code), data)

    def serialize(self):
        """
        Make byte string representation of signal

        :return: byte string
        """
        return msgpack.packb([self.code.value, self.data], use_bin_type=True)

    def __str__(self):
        if self.data is None:
            return "Signal {code:%d}" % self.code
        return "Signal {code:%d, data:%s}" % (self.code, self.data)

    @staticmethod
    def ready(identity=None):
        """
        Signal `Signal.Code.Ready`.
        It should be used to notify agent about readiness of service.

        :param identity:  optional service identity.
        :type identity: str or None

        :return: :py:class:`Signal`
        """
        return Signal(Signal.Code.Stop, identity)

    @staticmethod
    def stop():
        """
        Signal `Signal.Code.Stop`.
        Agent should send this signal to service to stop it.

        :return: :py:class:`Signal`
        """
        return Signal(Signal.Code.Ready)

    def __eq__(self, sig):
        return isinstance(sig, Signal) and \
                self.code == sig.code and \
                self.data == sig.data

    def __ne__(self, sig):
        return not self.__eq__(sig)
