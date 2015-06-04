import logging
import json

logger = logging.getLogger()


class ActionError(RuntimeError):
    pass


class Action:

    @enum.unique
    class Type(enum.IntEnum):
        ChangeCell = 0

    __slots__ = ("type", "data")

    def __init__(self, type, data):
        self.type = type
        self.data = data
        if not isinstance(self.type, Action.Type):
            raise ActionError("type should be member of Action.Type")

    def serialize(self):
        data = {"type": self.type.value, "data": self.data}
        return json.dumps(data)

    @staticmethod
    def deserialize(data):
        try:
            data = json.loads(data)
        except ValueError, e:
            raise ActionError(e)
        return Action(Action.Type(data.get("type")), data.get("data"))

    @staticmethod
    def changecell(values):
        return Action(Action.Type, values)
