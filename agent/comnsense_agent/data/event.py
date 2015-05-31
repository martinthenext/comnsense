import logging
import json

logger = logging.getLogger(__name__)

EVENT_WORKBOOK_OPEN = 0
EVENT_WORKBOOK_BEFORE_CLOSE = 1
EVENT_SHEET_CHANGE = 2

EVENTS = [
    EVENT_WORKBOOK_OPEN,
    EVENT_WORKBOOK_BEFORE_CLOSE,
    EVENT_SHEET_CHANGE
]


class EventError(RuntimeError):
    pass


class Event:
    __slots__ = ("type", "workbook", "sheet", "values")

    def __init__(self, *args):
        for name, value in zip(self.__slots__, args):
            setattr(self, name, value)
        if self.type not in EVENTS:
            raise EventError("unknown event type")

    def serialize(self):
        data = {name: getattr(self, name) for name in self.__slots__}
        return json.dumps(data)

    @staticmethod
    def deserialize(payload):
        data = None
        try:
            data = json.loads(payload)
        except ValueError, e:
            raise EventError(e)
        type = data.get("type")
        if type is None:
            raise EventError("could not get event type")
        workbook = data.get("workbook")
        sheet = data.get("sheet")
        values = data.get("values")
        if values is None:
            values = []
        return Event(type, workbook, sheet, values)
