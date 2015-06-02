import logging
import json

logger = logging.getLogger(__name__)


class ResponseError(RuntimeError):
    pass


class Response:
    __slots__ = ("code", "data")

    def __init__(self, code, data):
        self.code = code
        self.data = data
        if code < 100 or code > 599:
            raise ResponseError("unknown response http code: %s", self.code)
        if not self.data:
            raise ResponseError("request data is empty")

    def serialize(self):
        data = {"code": self.code, "data": self.data}
        return json.dumps(data)

    @staticmethod
    def deserialize(data):
        try:
            data = json.loads(data)
        except ValueError, e:
            raise ResponseError(e)
        return Response(data.get("code"), data.get("data"))
