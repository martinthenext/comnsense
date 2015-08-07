import logging
import json
import enum

from comnsense_agent.data.cell import Cell
from comnsense_agent.data.data import Data
from comnsense_agent.utils.exception import convert_exception
from comnsense_agent.utils.serialization import JsonSerializable


logger = logging.getLogger()


class Action(JsonSerializable, Data):
    """
    Action is representation of some commands for addin.

    Action should be used to changing cell's value on worksheet.
    E.g. you can set new value *John* to cell *$A$2* on sheet *Contacts*:

    .. doctest::
       :options: +NORMALIZE_WHITESPACE

       >>> from comnsense_agent.data import Action, Cell
       >>> action = Action(
       ... Action.Type.ChangeCell,
       ... '6febeb82-3c86-11e5-baeb-3c07543b8a2e',
       ... 'Contacts',
       ... [[Cell('$A$2', 'John')]])
       >>> print action.serialize(indent=2)
       {
         "cells": [
           [
             {
               "key": "$A$2",
               "value": "John"
             }
           ]
         ],
         "sheet": "Contacts",
         "type": 0,
         "workbook": "6febeb82-3c86-11e5-baeb-3c07543b8a2e"
       }
    """

    @enum.unique
    class Type(enum.IntEnum):
        """
        Action type enumeration

        .. attribute:: ChangeCell

           Change some cells on worksheet

        .. attribute:: RangeRequest

           Request some cells from worksheet

        """

        ChangeCell = 0
        RangeRequest = 1

    @enum.unique
    class Flags(enum.IntEnum):
        """
        Action flags enumeration

        .. attribute:: NoFlags

           Default value, no extra flags

        .. attribute:: RequestColor

           Request cell's background color

           .. note::

              in `RangeRequest <Action.Type.RangeRequest>` only

        .. attribute:: RequestFont

           Request font name of cell

           .. note::

              in `RangeRequest <Action.Type.RangeRequest>` only

        .. attribute:: RequestFontstyle

           Request style (italic, bold, underline) of cell's font

           .. note::

              in `RangeRequest <Action.Type.RangeRequest>` only

        .. attribute:: RequestBorders

           Request cell's borders

           .. note::

              in `RangeRequest <Action.Type.RangeRequest>` only

        """
        NoFlags = 0
        RequestColor = 1
        RequestFont = 2
        RequestFontstyle = 4
        RequestBorders = 8

    __slots__ = ("_type", "_workbook", "_sheet", "_content", "_flags")

    def __init__(self, type, workbook, sheet, content, flags=None):
        self._type = type
        self._workbook = workbook
        self._sheet = sheet
        self._content = content
        self._flags = flags or Action.Flags.NoFlags
        self.validate()

    def validate(self):
        if not isinstance(self._type, Action.Type):
            raise Data.ValidationError("type should be member of Action.Type")
        if not self._workbook:
            raise Data.ValidationError("workbook should not be empty")
        if not self._sheet:
            raise Data.ValidationError("sheet should not be empty")
        if not self._content:
            raise Data.ValidationError("content (%s) should not be empty" %
                                       self._get_content_name())

        if self._type == Action.Type.ChangeCell:
            self._type = Action.Flags.NoFlags

        if isinstance(self._flags, Action.Flags):
            self._flags = self._flags.value

        if self._type == Action.Type.ChangeCell and \
                not isinstance(self._content, list):
            raise Data.ValidationError("%s should be a list" %
                                       self._get_content_name())

        if self._type == Action.Type.RangeRequest and \
                not isinstance(self._content, (unicode, str)):
            raise Data.ValidationError("%s should be a str" %
                                       self._get_content_name())

        if not 0 <= self._flags <= self._get_max_flags():
            raise Data.ValidationError(
                "flags cannot be greater than %d and less that %d" %
                (self._get_max_flags(), Action.Flags.NoFlags.value))

    def _get_content_name(self):
        if self._type == self.Type.ChangeCell:
            return "cells"
        elif self._type == self.Type.RangeRequest:
            return "rangeName"

    def _get_max_flags(self):
        return sum(map(lambda x: x.value,
                       Action.Flags.__members__.values()))

    @property
    def type(self):
        """
        Action `type <Action.Type>`
        """
        return self._type

    @property
    def workbook(self):
        """
        The id of the workbook that should receive this action
        """
        return self._workbook

    @property
    def sheet(self):
        """
        The sheet name to which action should be applied
        """
        return self._sheet

    @property
    def range_name(self):
        """
        Requested range name

        .. note::

           in `RangeRequest <Action.Type.RangeRequest>` only
        """
        if self._type != Action.Type.RangeRequest:
            return None
        return self._content

    @property
    def cells(self):
        """
        The sequence of cells which should be changed

        .. note::

           in `ChangeCell <Action.Type.ChangeCell>` only
        """
        if self._type != Action.Type.ChangeCell:
            return None
        return self._content

    @property
    def flags(self):
        """
        Action modification `flags <Action.Flags>`
        """
        return self._flags

    def __getstate__(self):
        state = {
            "type": self._type.value,
            "workbook": self._workbook,
            "sheet": self._sheet
        }

        if self._flags != Action.Flags.NoFlags.value:
            state["flags"] = self._flags

        if self._type == Action.Type.ChangeCell:
            state[self._get_content_name()] = \
                Cell.table_to_primitive(self._content)
        elif self._type == Action.Type.RangeRequest:
            state[self._get_content_name()] = self._content
        else:
            raise NotImplementedError("unknown type: %s" % repr(self._type))

        return state

    def __setstate__(self, state):
        self._type = Action.Type(state.get("type"))
        self._workbook = state.get("workbook")
        self._sheet = state.get("sheet")

        if self._type == Action.Type.ChangeCell:
            self._content = Cell.table_from_primitive(
                state.get(self._get_content_name()))
        elif self._type == Action.Type.RangeRequest:
            self._content = state.get(self._get_content_name())
        else:
            raise NotImplementedError("unknown type: %s" % repr(self._type))

        self._flags = state.get("flags", Action.Flags.NoFlags)
        self.validate()

    @staticmethod
    def change(workbook, sheet, cells):
        """
        Static constructor for `Action.Type.ChangeCell`.

        :param workbook: `workbook id <Action.workbook>`
        :param sheet:    `sheet name <Action.sheet>`
        :param cells:    `chaged cells <Action.cells>`

        :return: `Action`
        """
        return Action(Action.Type.ChangeCell, workbook, sheet, cells)

    @staticmethod
    def change_from_event(event, cells):
        """
        Static constructor for `Action.Type.ChangeCell`.

        :param event: event `Event` - `SheetChange <Event.Type.SheetChange>`
                      or `RangeRequest <Event.Type.RangeResponse>`
        :param cells: `changed cells <Action.cells>`

        :return: `Action`
        """
        return Action(
            Action.Type.ChangeCell, event.workbook, event.sheet, cells)

    @staticmethod
    def request(workbook, sheet, range_name, flags=None):
        """
        Static constructor for `Action.Type.RangeRequest`.

        :param workbook:   `workbook id <Action.workbook>`
        :param sheet:      `sheet name <Action.sheet>`
        :param range_name: `requested range <Action.range_name>`
        :param flags:      `modification flags <Action.Flags>`

        :return: `Action`
        """
        return Action(
            Action.Type.RangeRequest, workbook, sheet, range_name, flags)

    @staticmethod
    def request_from_event(event, range_name, flags=None):
        """
        Static constructor for `Action.Type.RangeRequest`.

        :param event:    event `Event` - `SheetChange <Event.Type.SheetChange>`
                           or `RangeRequest <Event.Type.RangeResponse>`
        :param range_name: `requested range <Action.range_name>`
        :param flags:      `modification flags <Action.Flags>`

        :return: `Action`
        """
        return Action(
            Action.Type.RangeRequest, event.workbook,
            event.sheet, range_name, flags)

    def __repr__(self):
        return self.serialize()

    def __str__(self):
        return repr(self)
