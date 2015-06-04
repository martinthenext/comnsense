import logging
import json
import msgpack

logger = logging.getLogger(__name__)


class ResponseError(RuntimeError):
    pass


class Response:
    __slots__ = ("code", "data")

    def __init__(self, code, data=None):
        self.code = code
        self.data = data
        if code < 100 or code > 599:
            raise ResponseError("unknown response http code: %s", self.code)

    def serialize(self):
        return msgpack.packb([self.code, self.data], use_bin_type=True)

    @staticmethod
    def deserialize(data):
        return Response(*msgpack.unpackb(data, encoding='utf-8'))

    @staticmethod
    def accepted():
        return Response(202)

    @staticmethod
    def created():
        return Response(201)

    @staticmethod
    def nocontent():
        return Response(204)

    @staticmethod
    def ok(data):
        return Response(200, data)

    @staticmethod
    def notfound():
        return Response(404)
