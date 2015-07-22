import logging

logger = logging.getLogger(__name__)


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
