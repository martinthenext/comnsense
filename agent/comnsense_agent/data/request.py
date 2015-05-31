import logging

logger = logging.getLogger(__name__)


REQUEST_AUTH = 0
REQUEST_GETID = 1
REQUEST_GETMODEL = 2

REQUESTS = [
    REQUEST_GETID,
    REQUEST_GETMODEL,
]


class RequestError(RuntimeError):
    pass


class Request:
    __slots__ = ("type", "data")

    URLS = {
        REQUEST_AUTH: "agent/auth",
        REQUEST_GETID: "agent/register",
        REQUEST_GETMODEL: "agent/model",
    }

    METHODS = {
        REQUEST_AUTH: "POST",
        REQUEST_GETID: "PUT",
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
        return RequestError(data.get("type"), data.get("data"))

    def get_url(self):
        Request.URLS[self.type]

    def get_method(self):
        Request.METHODS[self.type]

    def get_body(self):
        return json.dumps(self.data)

    @staticmethod
    def getid(data):
        return Request(REQUEST_GETID, data)

    @staticmethod
    def getmodel(workbook):
        return Request(REQUEST_GETMODEL, {"workbook": workbook})
