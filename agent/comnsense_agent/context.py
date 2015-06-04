import logging
import copy

logger = logging.getLogger(__name__)


class Context(object):
    def __init__(self):
        self._copy = None
        self._workbook = None
        self._ready = False

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
