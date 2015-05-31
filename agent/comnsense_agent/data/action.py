import logging
import json

logger = logging.getLogger()


ACTION_SETID = 0
ACTION_CHANGE_CELL = 1

ACTIONS = [
    ACTION_SETID,
    ACTION_CHANGE_CELL,
]


class ActionError(RuntimeError):
    pass


class Action:
    __slots__ = ("type", "data")

    def __init__(self, type, data):
        self.type = type
        self.data = data
        if self.type not in ACTIONS:
            raise ActionError("unknown action type: %s", self.type)

    def serialize(self):
        data = {"type": self.type, "data": self.data}
        return json.dumps(data)

    @staticmethod
    def deserialize(data):
        try:
            data = json.loads(data)
        except ValueError, e:
            raise ActionError(e)
        return Action(data.get("type"), data.get("data"))

    @staticmethod
    def setid(workbook):
        return Action(ACTION_SETID, workbook)
