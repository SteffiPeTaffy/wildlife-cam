import time
from multiprocessing import Process


class Worker(Process):
    def __init__(self, queue, queue_function, *args, **kwargs):
        self.queue = queue
        self.queue_function = queue_function
        super().__init__(*args, **kwargs)

    def run(self):
        while True:
            time.sleep(1)
            if not self.queue.empty():
                queue_item = self.queue.get(timeout=3)
                self.queue_function(queue_item)
