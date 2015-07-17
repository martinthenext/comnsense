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

        .. py:attribute:: RangeResponse

           response for `Action.Type.RangeRequest`

        """

        WorkbookOpen = 0
        WorkbookBeforeClose = 1
        SheetChange = 2
        RangeResponse = 3

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

        data = {}
        data["type"] = self.type.value
        data["workbook"] = self.workbook
        if self.sheet:
            data["sheet"] = self.sheet
        if self.cells:
            data["cells"] = Cell.table_to_primitive(self.cells)
        if self.prev_cells:
            data["prev_cells"] = Cell.table_to_primitive(self.prev_cells)
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
                    logger.debug("key in deserialize method: %s", repr(key))
                    dct[key] = Cell.table_from_primitive(dct[key])
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
        logger.debug("cells in deserialize method: %s", repr(cells))
        prev_cells = data.get("prev_cells")
        return Event(type, workbook, sheet, cells, prev_cells)

    def _get_rows(self, cells):
        rows = {}
        for row in cells:
            for cell in row:
                row.setdefault(cell.row, []).append(cell)
        return rows

    def _get_columns(self, cells):
        columns = {}
        for row in cells:
            for cell in row:
                columns.setdefault(cell.column, []).append(cell)
        return columns

    @property
    def rows(self):
        return self._get_rows(self.cells)

    @property
    def prev_rows(self):
        return self._get_rows(self.prev_cells)

    @property
    def columns(self):
        return self._get_columns(self.cells)

    @property
    def prev_columns(self):
        logger.debug("prev_cells: %s", repr(self.prev_cells))
        return self._get_columns(self.prev_cells)

    @property
    def previous(self, cell):
        row = sef.prev_rows.get(cell.row)
        if row is None:
            return None
        row = [x for x in row if x.key == cell.key]
        if not row:
            return None
        return row[0]

    def __eq__(self, another):
        for attr in Event.__slots__:
            if getattr(self, attr) != getattr(another, attr):
                return False
        return True

    def __ne__(self, another):
        return not self.__eq__(another)
