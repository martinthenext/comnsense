import enum
import logging
import msgpack
import types

from .data import Data
from comnsense_agent.utils.exception import convert_exception

logger = logging.getLogger(__name__)


class Signal(Data):
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

    __slots__ = ("_code", "_data")

    def __init__(self, code, data=None):
        self._code = code
        self._data = data
        self.validate()

    @property
    def code(self):
        return self._code

    @property
    def data(self):
        return self._data

    def validate(self):
        if not isinstance(self._code, Signal.Code):
            raise Data.ValidationError("code should be member of Signal.Code")
        if self._code == Signal.Code.Stop and self._data is not None:
            raise Data.ValidationError("no data for Signal.Stop")
        if not isinstance(self._data, (int, str, types.NoneType)):
            raise Data.ValidationError("data should be a str")

    @staticmethod
    @convert_exception(Data.SerializationError)
    def deserialize(data):
        """
        Creates :py:class:`Signal` from byte string representation

        :param str data: Byte string representation
        :return: :py:class:`Signal` object
        """
        code, data = msgpack.unpackb(data, encoding='utf-8')
        return Signal(Signal.Code(code), data)

    @convert_exception(Data.SerializationError)
    def serialize(self):
        """
        Make byte string representation of signal

        :return: byte string
        """
        return msgpack.packb([self.code.value, self.data], use_bin_type=True)

    def __repr__(self):
        if self._data is None:
            return "Signal {code:%d}" % self._code
        return "Signal {code:%d, data:%s}" % (self._code, self._data)

    @staticmethod
    def ready(identity=None):
        """
        Signal `Signal.Code.Ready`.
        It should be used to notify agent about readiness of service.

        :param identity:  optional service identity.
        :type identity: str or None

        :return: :py:class:`Signal`
        """
        return Signal(Signal.Code.Ready, identity)

    @staticmethod
    def stop():
        """
        Signal `Signal.Code.Stop`.
        Agent should send this signal to service to stop it.

        :return: :py:class:`Signal`
        """
        return Signal(Signal.Code.Stop)
