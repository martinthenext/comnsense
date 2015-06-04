import logging
import json
import enum

logger = logging.getLogger(__name__)


class EventError(RuntimeError):
    pass


class Event:

    @enum.unique
    class Type(enum.IntEnum):
        WorkbookOpen = 0
        WorkbookBeforeClose = 1
        SheetChange = 2

    __slots__ = ("type", "workbook", "sheet", "values")

    def __init__(self, *args):
        for name, value in zip(self.__slots__, args):
            setattr(self, name, value)
        if not isinstance(self.type, Event.Type):
            raise EventError("type should be member of Event.Type")
        if not self.workbook:
            raise EventError("workbook should not be empty")
        if self.values is None:
            self.values = []

    def serialize(self):
        data = {name: getattr(self, name) for name in self.__slots__}
        data["type"] = self.type.value
        return json.dumps(data)

    @staticmethod
    def deserialize(payload):
        data = None
        try:
            data = json.loads(payload)
        except ValueError, e:
            raise EventError(e)
        type = Event.Type(data.get("type"))
        workbook = data.get("workbook")
        sheet = data.get("sheet")
        values = data.get("values")
        return Event(type, workbook, sheet, values)
