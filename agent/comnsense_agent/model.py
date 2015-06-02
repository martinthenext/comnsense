import logging

logger = logging.getLogger(__name__)


class Model:
    def __init__(self):
        self._workbook = None

    def _get_workbook_id(self):
        return self._workbook

    def _set_workbook_id(self, workbook):
        self._workbook = workbook

    # model may be too complex, so lets define getter and setter
    workbook = property(_get_workbook_id, _set_workbook_id)

    def dumps(self):
        """
        Creates byte string representation of `Model`.
        Algorithm should not serialize workbook_id,
        it can be used as key for serialization/deserialization
        :returns: byte string
        """
        return b""

    def loads(self, data):
        """
        Constructs `Model` object from byte string
        :returns: `Model`
        """

    def __eq__(self, model):
        # TODO write here something sensible
        # It is needed for tests
        return isinstance(model, Model)

    def __ne__(self, model):
        return not self.__eq__(model)
