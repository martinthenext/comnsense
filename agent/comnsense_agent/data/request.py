import logging
import json

logger = logging.getLogger(__name__)


REQUEST_AUTH = 0
REQUEST_GETMODEL = 1
REQUEST_SAVEMODEL = 2

REQUESTS = [
    REQUEST_AUTH,
    REQUEST_GETMODEL,
    REQUEST_SAVEMODEL,
]


class RequestError(RuntimeError):
    pass


class Request:
    __slots__ = ("type", "data")

    URLS = {
        REQUEST_AUTH: "agent/auth",
        REQUEST_GETMODEL: "agent/context/%(workbook)s",
        REQUEST_SAVEMODEL: "agent/context/%(workbook)s",
    }

    METHODS = {
        REQUEST_AUTH: "POST",
        REQUEST_GETMODEL: "GET",
        REQUEST_SAVEMODEL: "POST",
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
        return Request.URLS[self.type] % self.data

    def get_method(self):
        return Request.METHODS[self.type]

    def get_body(self):
        return json.dumps(self.data)

    @staticmethod
    def getcontext(workbook):
        return Request(
            REQUEST_GETMODEL, {"workbook": workbook})

    @staticmethod
    def savecontext(workbook, context):
        return Request(
            REQUEST_GETMODEL, {"workbook": workbook, "context": context})
