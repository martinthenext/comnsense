import logging
import json
import enum

from comnsense_agent.data.cell import Cell


logger = logging.getLogger(__name__)


class EventError(RuntimeError):
    pass


class Event(object):
    """
    Events should be used for transferring data between from the Excel
    to the `Agent`
    """

    @enum.unique
    class Type(enum.IntEnum):
        """
        Event type enumeration

        .. py:attribute:: WorkbookOpen

           first event from workbook, contains only workbook id

        .. py:attribute:: WorkbookBeforeClose

           last event from workbook, contains only workbook id

        .. py:attribute:: SheetChange

           one or more cells was changed, contains workbook id,
           changed sheet id and list of changed cell with new data
        """

        WorkbookOpen = 0
        WorkbookBeforeClose = 1
        SheetChange = 2

    __slots__ = ("type", "workbook", "sheet", "cells", "prev_cells")

    def __init__(self, *args):
        for name, value in zip(self.__slots__[:len(args)], args):
            setattr(self, name, value)
        if not isinstance(self.type, Event.Type):
            raise EventError("type should be member of Event.Type")
        if not self.workbook:
            raise EventError("workbook should not be empty")
        if not hasattr(self, "sheet"):
            self.sheet = None
        if not hasattr(self, "cells") or self.cells is None:
            self.cells = []
        if not hasattr(self, "prev_cells") or self.prev_cells is None:
            self.prev_cells = []

    def serialize(self):
        """
        Make byte string representation of event

        :return: byte string
        """

        data = {name: getattr(self, name) for name in self.__slots__}
        data["type"] = self.type.value
        data["cells"] = Cell.table_to_python_object(self.cells)
        data["prev_cells"] = Cell.table_to_python_object(self.prev_cells)
        return json.dumps(data)

    @staticmethod
    def deserialize(payload):
        """
        Creates :py:class:`Event` from byte string representation

        :param str data: Byte string representation
        :return: :py:class:`Event` object
        """

        def hook(dct):
            for key in ["cells", "prev_cells"]:
                if key in dct:
                    dct[key] = Cell.table_from_python_object(dct[key])
                return dct

        data = None
        try:
            data = json.loads(payload, object_hook=hook)
        except ValueError, e:
            raise EventError(e)
        type = Event.Type(data.get("type"))
        workbook = data.get("workbook")
        sheet = data.get("sheet")
        cells = data.get("cells")
        prev_cells = data.get("prev_cells")
        return Event(type, workbook, sheet, cells, prev_cells)
