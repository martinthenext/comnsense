import logging

logger = logging.getLogger(__name__)


class Multiplexer(object):
    def merge(self, event, actions):
        raise NotImplementedError("abstract method was called")
