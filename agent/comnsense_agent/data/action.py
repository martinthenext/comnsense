import logging
import json
import enum

from comnsense_agent.data.cell import Cell
from comnsense_agent.utils.exception import convert_exception


logger = logging.getLogger()


class ActionError(RuntimeError):
    pass


class Action(object):
    """
    Action is representation some commands for Excel's addin
    """

    @enum.unique
    class Type(enum.IntEnum):
        """
        Action type enumeration

        .. py:attribute:: ChangeCell

        change some cells on worksheet

        .. py:attribute:: RangeRequest

        request cells from worksheet

        """

        ChangeCell = 0
        RangeRequest = 1

    @enum.unique
    class Flags(enum.IntEnum):
        """
        Action flags enumeration

        .. py:attribute:: RequestColor

        request color of cell's font

           .. note::

           in `Action.Type.RangeRequest` only

        .. py:attribute:: RequestFont

        request font name of cell

           .. note::

           in `Action.Type.RangeRequest` only

        .. py:attribute:: RequestFontstyle

        request style (italic, bold, underline) of cell's font

           .. note::

           in `Action.Type.RangeRequest` only

        .. py:attribute:: RequestBorders

        reques cell's borders

           .. note::

           in `Action.Type.RangeRequest` only

        """

        RequestColor = 1
        RequestFont = 2
        RequestFontstyle = 4
        RequestBorders = 8

    __slots__ = ("type", "workbook", "sheet", "arg", "flags")

    @convert_exception(ActionError)
    def __init__(self, *args):
        for name, value in zip(self.__slots__[:len(args)], args):
            setattr(self, name, value)
        if not isinstance(self.type, Action.Type):
            raise ActionError("type should be member of Action.Type")
        if not self.workbook:
            raise ActionError("workbook should not be empty")
        if not hasattr(self, "sheet"):
            raise ActionError("sheet should not be empty")
        if not hasattr(self, "arg") or self.arg is None:
            if self.type == Action.Type.ChangeCell:
                self.arg = []
            elif self.type == Action.Type.RangeRequest:
                self.arg = ""
        if not hasattr(self, "flags") or self.flags is None:
            self.flags = 0

        assert ((self.type == Action.Type.ChangeCell and
                 isinstance(self.arg, list)) or
                (self.type == Action.Type.RangeRequest and
                 isinstance(self.arg, (unicode, str))))

    @property
    def range_name(self):
        if self.type != Action.Type.RangeRequest:
            return None
        return self.arg

    @range_name.setter
    @convert_exception(ActionError)
    def range_name(self, value):
        assert isinstance(value, (unicode, str))
        assert self.type == Action.Type.RangeRequest
        self.arg = value

    @property
    def cells(self):
        if self.type != Action.Type.ChangeCell:
            return None
        return self.arg

    @cells.setter
    @convert_exception(ActionError)
    def cells(self, value):
        assert isinstance(value, list)
        assert self.type == Action.Type.ChangeCell
        self.arg = value

    @convert_exception(ActionError)
    def serialize(self):
        data = {"type": self.type.value,
                "workbook": self.workbook,
                "sheet": self.sheet}
        if self.flags > 0:
            data["flags"] = self.flags
        if self.type == Action.Type.ChangeCell:
            data["cells"] = Cell.table_to_primitive(self.arg)
        elif self.type == Action.Type.RangeRequest:
            data["rangeName"] = self.arg
        return json.dumps(data)

    @staticmethod
    @convert_exception(ActionError)
    def deserialize(data):

        def hook(dct):
            key = "cells"
            if key in dct:
                dct[key] = Cell.table_from_primitive(dct[key])
            return dct

        try:
            data = json.loads(data, object_hook=hook)
        except ValueError, e:
            raise ActionError(e)
        type = Action.Type(data.get("type"))
        workbook = data.get("workbook")
        sheet = data.get("sheet")
        arg = None
        if type == Action.Type.ChangeCell:
            arg = data.get("cells")
        elif type == Action.Type.RangeRequest:
            arg = data.get("rangeName")
        flags = data.get("flags")
        return Action(type, workbook, sheet, arg, flags)

    @staticmethod
    def change(workbook, sheet, cells, flags=0):
        return Action(Action.Type.ChangeCell, workbook, sheet, cells, flags)

    @staticmethod
    def change_from_event(event, cells, flags=0):
        return Action(
            Action.Type.ChangeCell, event.workbook,
            event.sheet, cells, flags)

    @staticmethod
    def request(workbook, sheet, range_name, flags=0):
        return Action(
            Action.Type.RangeRequest, workbook, sheet, range_name, flags)

    @staticmethod
    def request_from_event(event, range_name, flags=0):
        return Action(
            Action.Type.RangeRequest, event.workbook,
            event.sheet, range_name, flags)

    def __eq__(self, another):
        for attr in Action.__slots__:
            if getattr(self, attr) != getattr(another, attr):
                return False
        return True

    def __ne__(self, another):
        return not self.__eq__(another)
