import enum
import logging
import types

from .data import Data
from comnsense_agent.utils.exception import convert_exception
from comnsense_agent.utils.serialization import MsgpackSerializable

logger = logging.getLogger(__name__)


class Signal(MsgpackSerializable, Data):
    """
    Signals should be used for service messages in interservice communication.
    It shall not contain the data if possible.
    """

    @enum.unique
    class Code(enum.IntEnum):
        """
        Signal code enumeration

        .. attribute:: Stop

           Stop signal code

        .. attribute:: Ready

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
        """
        Signal `code <Signal.Code>`
        """
        return self._code

    @property
    def data(self):
        """
        Signal data
        """
        return self._data

    def validate(self):
        if not isinstance(self._code, Signal.Code):
            raise Data.ValidationError("code should be member of Signal.Code")
        if self._code == Signal.Code.Stop and self._data is not None:
            raise Data.ValidationError("no data for Signal.Stop")
        if not isinstance(self._data, (int, str, types.NoneType)):
            raise Data.ValidationError("data should be a str")

    @staticmethod
    def ready(identity=None):
        """
        Static constructor for `Signal.Code.Ready`.
        It should be used to notify agent about readiness of service.

        :param identity: optional service identity.
        :type identity: str or None

        :return: `Signal`
        """
        return Signal(Signal.Code.Ready, identity)

    @staticmethod
    def stop():
        """
        Static constructor for `Signal.Code.Stop`.
        Agent should send this signal to service to stop it.

        :return: `Signal`
        """
        return Signal(Signal.Code.Stop)

    def __getstate__(self):
        return [self._code.value, self._data]

    def __setstate__(self, state):
        code, self._data = state
        self._code = Signal.Code(code)
        self.validate()

    def __repr__(self):
        if self._data is None:
            return "Signal {code:%d}" % self._code
        return "Signal {code:%d, data:%s}" % (self._code, self._data)

    def __str__(self):
        return repr(self)
