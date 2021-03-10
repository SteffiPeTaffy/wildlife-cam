import time
from threading import Timer
from logzero import logger


class RemainingTimer(Timer):
    _time_until_call = None
    _started_at = None

    def __init__(self, time_until_call, func_to_be_called):
        self._time_until_call = time_until_call
        super().__init__(time_until_call, func_to_be_called)

    def start_timer(self):
        self._started_at = time.time()
        self.start()

    def elapsed(self):
        return time.time() - self._started_at

    def remaining(self):
        return self._time_until_call - self.elapsed()


class ResettableTimer:
    def __init__(self, interval, function, timeout, *args, **kwargs):
        self._interval = interval
        self._function = function
        self._timeout = timeout
        self._args = args
        self._kwargs = kwargs
        self._count = 1
        self._timer = Timer(self._interval, self._function, self._args, self._kwargs)

    def start(self):
        self._timer.start()

    def is_alive(self):
        return self._timer.is_alive()

    def cancel(self):
        self._timer.cancel()

    def reset(self):
        if self._count * self._interval < self._timeout:
            logger.info("wildlife-cam: Resetting timer, count: {}, interval: {}, timeout: {}".format(self._count,
                                                                                                     self._interval,
                                                                                                     self._timeout))
            self._timer.cancel()
            self._timer = Timer(self._interval, self._function, self._args, self._kwargs)
            self._timer.start()
            self._count += 1
