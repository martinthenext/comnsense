import logging
from functools import wraps, partial

logger = logging.getLogger(__name__)


def publicmethod(method):
    method.public_method = True
    return method


class PublicMethods(object):
    __slots__ = ("public_methods",)

    def __init__(self):
        self.public_methods = None

    def __get__(self, obj, objtype=None):
        if self.public_methods is not None:
            return self.public_methods

        self.public_methods = []
        if objtype is None:
            objtype = type(obj)

        for attrname, attrvalue in objtype.__dict__.iteritems():
            if hasattr(attrvalue, "public_method") and attrvalue.public_method:
                self.public_methods.append(attrname)

        return self.public_methods


class PublicMethodLookup(object):
    __slots__ = ("sequence",)

    def __init__(self, sequence):
        self.sequence = sequence

    def __getattr__(self, name):
        for handler in self.sequence:
            if name in type(handler).provides:
                return getattr(handler, name)
        raise AttributeError("no one handler provides method %s" % name)


class EventHandler(object):
    """
    EventHandler is the base class for all algorithms.
    """
    def handle(self, event, context):
        """
        This method implements all logic of algorithm.

        :param event: incoming event from excel
        :type event: ``Data.Event``

        :param context: globalstate with information about all sheets
        and handlers. ``EventHandler`` should not change context
        :type context: ``Context``

        :return: sequence of :py:class:`Data.Action`
        """

        raise NotImplementedError("abstract method was called")

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "provides"):
            cls.provides = PublicMethods()
        return object.__new__(cls, *args, **kwargs)
