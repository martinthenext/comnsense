import logging

logger = logging.getLogger(__name__)


class Data(object):
    """
    This is basic class for all data structures used in communication.
    """

    class ValidationError(RuntimeError):
        """
        Raised when `Data` instance contains an inconsistent values.
        """
        pass

    __slots__ = ()

    def validate(self):
        """
        Validate consistency of all fields in the structure.

        It should be called from ``__init__``, ``deserialize`` and other
        methods, that can change internal state of structure.

        :raises: `Data.ValidationError`.
        """
        raise NotImplementedError()

    def serialize(self):
        """
        Returns byte string representation of the structure.

        :return: str
        """
        raise NotImplementedError()

    @classmethod
    def deserialize(cls, data):
        """
        Create instance from byte string *data*.

        :param data: byte string object representation
        :type data:  str

        :return: instance of child of `Data`
        """
        raise NotImplementedError()

    def __eq__(self, another):
        if not isinstance(another, self.__class__):
            return False
        for attr in self.__slots__:
            if getattr(self, attr) != getattr(another, attr):
                return False
        return True

    def __ne__(self, another):
        return not self.__eq__(another)
