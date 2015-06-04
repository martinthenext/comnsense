import logging
import json
import enum

logger = logging.getLogger(__name__)


class EventError(RuntimeError):
    pass


class Event:
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

    __slots__ = ("type", "workbook", "sheet", "values")

    def __init__(self, *args):
        for name, value in zip(self.__slots__[:len(args)], args):
            setattr(self, name, value)
        if not isinstance(self.type, Event.Type):
            raise EventError("type should be member of Event.Type")
        if not self.workbook:
            raise EventError("workbook should not be empty")
        if not hasattr(self, "sheet"):
            self.sheet = None
        if not hasattr(self, "values") or self.values is None:
            self.values = {}

    def serialize(self):
        """
        Make byte string representation of event

        :return: byte string
        """

        data = {name: getattr(self, name) for name in self.__slots__}
        data["type"] = self.type.value
        return json.dumps(data)

    @staticmethod
    def deserialize(payload):
        """
        Creates :py:class:`Event` from byte string representation

        :param str data: Byte string representation
        :return: :py:class:`Event` object
        """
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
