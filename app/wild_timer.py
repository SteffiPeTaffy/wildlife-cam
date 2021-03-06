import time
from threading import Timer


class RemainingTimer(Timer):
    started_at = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def start_timer(self):
        self.started_at = time.time()
        self.start()

    def elapsed(self):
        return time.time() - self.started_at

    def remaining(self):
        return self.interval - self.elapsed()
