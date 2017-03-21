import functools
import logging
import time


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class LogWith(object):
    """
    Logging decorator that allows you to log with
    a specific logger or set one up on the go.
    """

    def __init__(self, logger=None):

        self.logger = logger
        self.start = time.time()

    def __call__(self, func):
        """Returns a wrapper that wraps func.
           The wrapper will log the entry and exit
           points of the function with specified level.
        """

        # set logger if it was not set earlier
        if not self.logger:
            self.logger = logging.getLogger(func.__module__)
            logging.basicConfig(**self.setConfig)

        @functools.wraps(func)
        def wrapper(*args, **kwds):
            self.logger.info(
                'Running {}\n\n'.format(func.__name__))

            f_result = func(*args, **kwds)
            msg = 'Duration {}'.format(
                time.strftime("%H:%M:%S", time.time() - self.start)
            )
            self.logger.info(msg)
            return f_result
        return wrapper
