import logging

logger = logging.getLogger(__name__)


class Data(object):
    class SerializationError(RuntimeError):
        pass

    class ValidationError(RuntimeError):
        pass

    __slots__ = ()

    def validate(self):
        raise NotImplementedError()

    def serialize(self):
        raise NotImplementedError()

    @staticmethod
    def deserialize(data):
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
