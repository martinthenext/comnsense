import logging

from .multiplexer import Multiplexer

logger = logging.getLogger(__name__)


class FirstAnswer(Multiplexer):
    def merge(self, event, answers):
        if not answers:
            return []
        for array in answers:
            if array:
                return array
        return []
