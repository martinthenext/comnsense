import logging
import json
import enum

logger = logging.getLogger()


class ActionError(RuntimeError):
    pass


class Action:

    @enum.unique
    class Type(enum.IntEnum):
        ChangeCell = 0
        RangeRequest = 1

    @enum.unique
    class Flags(enum.IntEnum):
        RequestColor = 1
        RequestFont = 2
        RequestFontstyle = 4
        RequestBorders = 8

    __slots__ = ("type", "workbook", "sheet", "cells", "flags")

    def __init__(self, *args):
        for name, value in zip(self.__slots__[:len(args)], args):
            setattr(self, name, value)
        if not isinstance(self.type, Action.Type):
            raise ActionError("type should be member of Action.Type")
        if not self.workbook:
            raise ActionError("workbook should not be empty")
        if not hasattr(self, "sheet"):
            raise ActionError("sheet should not be empty")
        if not hasattr(self, "cells") or self.cells is None:
            self.cells = []
        if not hasattr(self, "flags") or self.flags is None:
            self.flags = 0

    def serialize(self):
        data = {"type": self.type.value,
                "workbook": self.workbook,
                "sheet": self.sheet}
        if self.flags > 0:
            data["flags"] = self.flags
        data["cells"] = Cell.table_to_python_object(self.cells)
        return json.dumps(data)

    @staticmethod
    def deserialize(data):

        def hook(dct):
            key = "cells"
            if key in dct:
                dct[key] = Cell.table_from_python_object(dct[key])
            return dct

        try:
            data = json.loads(data, object_hook=hook)
        except ValueError, e:
            raise ActionError(e)
        type = Action.Type(data.get("type"))
        workbook = data.get("workbook")
        sheet = data.get("sheet")
        cells = data.get("cells")
        flags = data.get("flags")
        return Action(type, workbook, sheet, cells, flags)

    @staticmethod
    def change(workbook, sheet, cells):
        return Action(Action.Type.ChangeCell, workbook, sheet, cells)

    @staticmethod
    def change_from_event(event, cells, flags=0):
        return Action(
            Action.Type.ChangeCell, event.workbook,
            event.sheet, cells, flags)
