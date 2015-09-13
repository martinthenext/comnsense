import logging

logger = logging.getLogger(__name__)


class Multiplexer(object):

    def merge(self, event, answers):
        """
        Produce the signle answer from the answers of
        `event handlers <EventHandler>`.

        :param event: incomming event
        :type event: `Event`

        :param answers: sequence of answers
        :type event: sequence of `Action` lists

        :return: list of `actions <Action>`
        """
        raise NotImplementedError("abstract method was called")
