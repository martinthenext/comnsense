import logging
import msgpack
import httplib

from comnsense_agent.data.data import Data
from comnsense_agent.utils.serialization import MsgpackSerializable


logger = logging.getLogger(__name__)


class Response(MsgpackSerializable, Data):
    """
    Represents server response in inservice communication.

    Actually server response is usual HTTP response.
    But it seems to overkill to serialize it and redirect from
    service to service. At present only request code is meaningful.
    """

    __slots__ = ("_code", "_data")

    def __init__(self, code, data=None):
        self._code = code
        self._data = data
        self.validate()

    @property
    def code(self):
        """
        HTTP code.

        .. seealso::

            Documentation for `httplib library
            <https://docs.python.org/2/library/httplib.html>`_
        """
        return self._code

    @property
    def data(self):
        """
        Some meaningful data. Usually ``None``.
        """
        return self._data

    def validate(self):
        if self._code not in httplib.responses:
            raise Data.ValidationError("unknown HTTP code: %s", self._code)

    def __getstate__(self):
        return [self._code, self._data]

    def __setstate__(self, state):
        self._code, self._data = state
        self.validate()

    @staticmethod
    def accepted():
        """
        Static constructor for ``Accepted`` response.
        """
        return Response(202)

    @staticmethod
    def created():
        """
        Static constructor for ``Created`` response.
        """
        return Response(201)

    @staticmethod
    def nocontent():
        """
        Static constructor for ``No Content`` response.
        """
        return Response(204)

    @staticmethod
    def ok(data=None):
        """
        Static constructor for ``OK`` response.
        """
        return Response(200, data)

    @staticmethod
    def notfound():
        """
        Static constructor for ``Not Found`` response.
        """
        return Response(404)

    def __repr__(self):
        return u"Response: %d %s" % (self._code, repr(self._data) or u"")

    def __str__(self):
        return repr(self)
