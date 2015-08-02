import enum
import json
import logging

from .data import Data
from comnsense_agent.data.cell import Cell
from comnsense_agent.utils.serialization import JsonSerializable


logger = logging.getLogger(__name__)


class Event(JsonSerializable, Data):
    """
    Events should be used for transferring data from the Excel to the `Agent`
    """

    @enum.unique
    class Type(enum.IntEnum):
        """
        Event type enumeration

        .. py:attribute:: WorkbookOpen

           First event from workbook, contains only workbook id

        .. py:attribute:: WorkbookBeforeClose

           Last event from workbook, contains only workbook id

        .. py:attribute:: SheetChange

           One or more cells was changed, contains workbook id,
           changed sheet id and list of changed cell with new data

        .. py:attribute:: RangeResponse

           Response for `Action.Type.RangeRequest`

        """

        WorkbookOpen = 0
        WorkbookBeforeClose = 1
        SheetChange = 2
        RangeResponse = 3

    __slots__ = ("_type", "_workbook", "_sheet", "_cells", "_prev_cells")

    def __init__(self, type, workbook, *args):
        self._type = type
        self._workbook = workbook
        for name, value in zip(self.__slots__[2:len(args) + 2], args):
            setattr(self, name, value)
        self.validate()

    @property
    def type(self):
        """
        Event `type <Event.Type>`
        """
        return self._type

    @property
    def workbook(self):
        """
        The id of the workbook that sent this event
        """
        return self._workbook

    @property
    def sheet(self):
        """
        The name of the sheet on which the event occurred
        """
        if self._type in (Event.Type.SheetChange, Event.Type.RangeResponse):
            return self._sheet

    @property
    def cells(self):
        """
        The sequence of `cells <Cell>`
        """
        if self._type in (Event.Type.SheetChange, Event.Type.RangeResponse):
            return self._cells

    @property
    def prev_cells(self):
        """
        The sequence of previous `cells <Cell>`

        .. note::
           Available only if type is SheetChange
        """
        if self._type == Event.Type.SheetChange:
            return self._prev_cells

    def validate(self):
        if not isinstance(self._type, Event.Type):
            raise Data.ValidationError("type should be member of Event.Type")
        if not self._workbook:
            raise Data.ValidationError("workbook should not be empty")
        if not hasattr(self, "_sheet"):
            self._sheet = None
        if not hasattr(self, "_cells") or self._cells is None:
            self._cells = []
        if not hasattr(self, "_prev_cells") or self._prev_cells is None:
            self._prev_cells = []
        if self._type in (Event.Type.SheetChange, Event.Type.RangeResponse):
            if self._sheet is None:
                raise Data.ValidationError(
                    "sheet should not be empty")
            if self._cells == []:
                raise Data.ValidationError(
                    "cells should contain at least one cell")
        else:
            self._sheet = None
            self._cells = []
            self._prev_cells = []

    def __getstate__(self):
        state = {}
        state["type"] = self._type.value
        state["workbook"] = self._workbook
        if self._sheet is not None:
            state["sheet"] = self._sheet
        if self._cells:
            state["cells"] = Cell.table_to_primitive(self._cells)
        if self._prev_cells:
            state["prev_cells"] = Cell.table_to_primitive(self._prev_cells)
        return state

    def __setstate__(self, state):
        self._type = Event.Type(state.get("type"))
        self._workbook = state.get("workbook")
        self._sheet = state.get("sheet")
        self._cells = Cell.table_from_primitive(
            state.get("cells", []))
        self._prev_cells = Cell.table_from_primitive(
            state.get("prev_cells", []))
        self.validate()

    def _get_rows(self, cells):
        rows = {}
        for row in cells:
            for cell in row:
                rows.setdefault(cell.row, []).append(cell)
        return rows

    def _get_columns(self, cells):
        columns = {}
        for row in cells:
            for cell in row:
                columns.setdefault(cell.column, []).append(cell)
        return columns

    @property
    def rows(self):
        if not self.cells:
            return {}
        return self._get_rows(self.cells)

    @property
    def prev_rows(self):
        if not self.prev_cells:
            return {}
        return self._get_rows(self.prev_cells)

    @property
    def columns(self):
        if not self.cells:
            return {}
        return self._get_columns(self.cells)

    @property
    def prev_columns(self):
        if not self.prev_cells:
            return {}
        return self._get_columns(self.prev_cells)

    def __repr__(self):
        return self.serialize()

    def __str__(self):
        return repr(self)
