import logging
import json
import enum

logger = logging.getLogger(__name__)


class RequestError(RuntimeError):
    pass


class Request:

    @enum.unique
    class Type(enum.IntEnum):
        Auth = 0
        GetContext = 1
        SaveContext = 2

    Url = {
        Type.Auth: "agent/auth",
        Type.GetContext: "agent/context/%(workbook)s",
        Type.SaveContext: "agent/context/%(workbook)s",
    }

    Method = {
        Type.Auth: "POST",
        Type.GetContext: "GET",
        Type.SaveContext: "POST",
    }

    __slots__ = ("type", "data")

    def __init__(self, type, data):
        self.type = type
        self.data = data
        if not isinstance(type, Request.Type):
            raise RequestError("type should be member of Request.Type")
        if not self.data:
            raise RequestError("data should not be empty")

    def serialize(self):
        data = {"type": self.type.value, "data": self.data}
        return json.dumps(data)

    @staticmethod
    def deserialize(data):
        try:
            data = json.loads(data)
        except ValueError, e:
            raise RequestError(e)
        return Request(Request.Type(data.get("type")), data.get("data"))

    def get_url(self):
        return Request.Url[self.type] % self.data

    def get_method(self):
        return Request.Method[self.type]

    def get_body(self):
        if self.type == Request.Type.GetContext:
            return ""
        elif self.type == Request.Type.SaveContext:
            return self.data["context"]
        else:
            return json.dumps(self.data)

    @staticmethod
    def getcontext(workbook):
        return Request(
            Request.Type.GetContext, {"workbook": workbook})

    @staticmethod
    def savecontext(workbook, context):
        return Request(
            Request.Type.SaveContext,
            {"workbook": workbook, "context": context})
