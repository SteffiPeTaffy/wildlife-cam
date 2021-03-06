import time
from threading import Timer


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
