import sys
import logging

logger = logging.getLogger(__name__)


def convert_exception(type, msg=""):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except:
                etype, evalue, tb = sys.exc_info()
                if etype == type and msg == "":
                    raise
                else:
                    if msg:
                        raise type("%s: %s" % (msg, evalue))
                    else:
                        raise type(evalue)
        return wrapper
    return decorator
