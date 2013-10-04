import logging
import sys


class Log:
    def __init__(self):
        raise NotImplementedError("Log is a static utility class and should not be instantiated.")

    @staticmethod
    def create_log(module):
        log = logging.getLogger(module)
        log.setLevel(logging.DEBUG)
        if len(log.handlers) == 0:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter("[%(asctime)s] [%(name)s] %(message)s", "%H:%M:%S"))
            log.addHandler(handler)
        return log