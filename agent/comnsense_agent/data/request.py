import logging
import json

logger = logging.getLogger(__name__)


REQUEST_AUTH = 0
REQUEST_GETMODEL = 1

REQUESTS = [
    REQUEST_GETMODEL,
]


class RequestError(RuntimeError):
    pass


class Request:
    __slots__ = ("type", "data")

    URLS = {
        REQUEST_AUTH: "agent/auth",
        REQUEST_GETMODEL: "agent/model",
    }

    METHODS = {
        REQUEST_AUTH: "POST",
        REQUEST_GETMODEL: "GET"
    }

    def __init__(self, type, data):
        self.type = type
        self.data = data
        if self.type not in REQUESTS:
            raise RequestError("unknown request type: %s", self.type)
        if not self.data:
            raise RequestError("request data is empty")

    def serialize(self):
        data = {"type": self.type, "data": self.data}
        return json.dumps(data)

    @staticmethod
    def deserialize(data):
        try:
            data = json.loads(data)
        except ValueError, e:
            raise RequestError(e)
        return Request(data.get("type"), data.get("data"))

    def get_url(self):
        Request.URLS[self.type]

    def get_method(self):
        Request.METHODS[self.type]

    def get_body(self):
        return json.dumps(self.data)

    @staticmethod
    def getmodel(workbook):
        return Request(REQUEST_GETMODEL, {"workbook": workbook})
