import enum
import logging
import msgpack

logger = logging.getLogger(__name__)


class RequestError(RuntimeError):
    pass


class Request(object):
    """
    Events should be used for transferring data between from the `Agent`
    to the Server
    """

    @enum.unique
    class Type(enum.IntEnum):
        GetContext = 0
        SaveContext = 1

    Url = {
        Type.GetContext: "agent/context/%(workbook)s",
        Type.SaveContext: "agent/context/%(workbook)s",
    }

    Method = {
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
        return msgpack.packb([self.type, self.data], use_bin_type=True)

    @staticmethod
    def deserialize(data):
        type, data = msgpack.unpackb(data, encoding='utf-8')
        return Request(Request.Type(type), data)

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
