import logging

from .multiplexer import Multiplexer

logger = logging.getLogger(__name__)


class FirstAnswer(Multiplexer):
    def merge(self, event, actions):
        if not actions:
            return []
        for array in actions:
            if array:
                return array
        return []
