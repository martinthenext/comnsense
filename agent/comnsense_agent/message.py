import logging

logger = logging.getLogger(__name__)

KIND_EVENT = "event"
KIND_ACTION = "action"
KIND_REQUEST = "request"
KIND_RESPONSE = "response"
KIND_LOG = "log"
KIND_SIGNAL = "signal"

KINDS = [
    KIND_EVENT,
    KIND_ACTION,
    KIND_REQUEST,
    KIND_RESPONSE,
    KIND_LOG,
    KIND_SIGNAL
]


class InvalidMessageError(RuntimeError):
    pass


class Message:
    NO_IDENT = "NO_IDENT"
    __slots__ = ("ident", "kind", "payload")

    def __init__(self, *message):
        if len(message) == 2:
            message = (Message.NO_IDENT, message[0], message[1])
        if hasattr(message[2], "serialize"):
            message = (message[0], message[1], message[2].serialize())
        for name, value in zip(self.__slots__, message):
            setattr(self, name, value)

        self.validate()
        logger.debug("done")

    def validate(self):
        logger.debug("validating message")
        if self.kind not in KINDS:
            raise InvalidMessageError(
                "unknown message kind: %s" % self.kind)
        # TODO validate ident here

    def __len__(self):
        if self.ident == Message.NO_IDENT:
            return len(self.__slots__) - 1
        return len(self.__slots__)

    def __getitem__(self, key):
        if isinstance(key, slice):
            shift = 0
            if self.ident == Message.NO_IDENT:
                shift = 1
            return [getattr(self, x) for x in
                    self.__slots__[key.start + shift: key.stop + shift]]
        if isinstance(key, int):
            key = self.__slots__[key]
        if key not in self.__slots__:
            raise KeyError("unknown part: %s" % key)
        return getattr(self, key)

    def __setitem__(self, key, value):
        if isinstance(key, int):
            key = self.__slots__[key]
        if key not in self.__slots__:
            raise KeyError("unknown part: %s" % key)
        setattr(self, key, value)
        self.validate()

    def __delitem__(self, key):
        raise KeyError("could not delete key: %s", key)

    def __iter__(self):
        shift = 0
        if self.ident == Message.NO_IDENT:
            shift = 1
        return (getattr(self, x) for x in self.__slots__[shift:])

    def __reversed__(self):
        raise NotImplementedError("could not reverse message")

    def __str__(self):
        if self.ident == Message.NO_IDENT:
            return "MSG {kind: %s, payload: %s}" % (self.kind, self.payload)
        return "MSG { ident:%s, kind:%s, payload:%s }" % (
            self.ident, self.kind, self.payload)

    def append(self, value):
        raise NotImplementedError("could not append to message")

    def head(self):
        return self.ident

    def last(self):
        return self.payload

    def is_action(self):
        return self.kind == KIND_ACTION

    def is_event(self):
        return self.kind == KIND_EVENT

    def is_request(self):
        return self.kind == KIND_REQUEST

    def is_response(self):
        return self.kind == KIND_RESPONSE

    def is_log(self):
        return self.kind == KIND_LOG

    def is_signal(self):
        return self.kind == KIND_SIGNAL

    @staticmethod
    def call(callback, log=None):
        if log is None:
            log = logger

        def oncall(message):
            try:
                msg = Message(*message)
                return callback(msg)
            except InvalidMessageError, e:
                log.warn(e)
            except Exception, e:
                log.exception(e)
        return oncall
