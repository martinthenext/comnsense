import logging

from comnsense_agent.data import Action
from comnsense_agent.message import Message

logger = logging.getLogger(__name__)


class Table(object):
    __slots__ = ("_sheet", "header", "stats")

    def __init__(self, sheet, header=None):
        self._sheet = sheet
        self.header = header
        self.stats = {}

    def request_header(self):
        header_range = "$A$1:$AZ$1"
        return Message.action(Action.request(
            self._sheet._context.workbook,
            self._sheet.name, header_range))

    def __repr__(self):
        if self.header is None:
            header = None
        else:
            header = ["%s: %s" % (cell.column, cell.value)
                      for cell in self.header]
        if not self.stats:
            stats = "{}"
        else:
            stats = {}
            for key, value in self.stats.items():
                if isinstance(value, dict):
                    stats[key] = value.keys()
                else:
                    raise NotImplementedError()
        result = u"Table {header: %s, stats: %s}" % (header, stats)
        return result.encode('utf-8')


class Sheet(object):
    __slots__ = ("_context", "name", "tables")

    def __init__(self, context, name, tables=None):
        self.name = name
        if tables is None:
            tables = []
        self.tables = tables
        self._context = context

    def __repr__(self):
        result = u"Sheet {name: %s, tables: %%s}" % self.name
        tables = [repr(t) for t in self.tables]
        result = result % tables
        return result.encode('utf-8')


class Context(object):
    def __init__(self):
        self._copy = None
        self._workbook = None
        self._ready = False
        self.sheets = {}

    @property
    def workbook(self):
        return self._workbook

    @workbook.setter
    def workbook(self, workbook):
        self._workbook = workbook

    def dumps(self):
        """
        Creates byte string representation of :py:class:`Context`.
        Algorithm should not serialize workbook_id,
        it can be used as key for serialization/deserialization

        :return: byte string
        """
        return b""

    def loads(self, data):
        """
        Constructs :py:class:`Context` object from byte string
        :return: :py:class:`Context`
        """
        if self._workbook:
            self._ready = True

    def is_ready(self):
        """
        True if model is ready to working with runtime,
        e.g.: when it was retrieved from server
        """
        # TODO write here something sensible
        return self._ready

    def __eq__(self, model):
        # TODO write here something sensible
        # It is needed for tests
        return isinstance(model, Context)

    def __ne__(self, model):
        return not self.__eq__(model)

    def __enter__(self):
        # TODO backup model
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # TODO rollback model to previous state in case of exception
            pass
        return exc_type is None
