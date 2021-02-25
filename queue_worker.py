import asyncio
from multiprocessing import Process


class Worker(Process):
    def __init__(self, queue, queue_function, *args, **kwargs):
        self.queue = queue
        self.queue_function = queue_function
        super().__init__(*args, **kwargs)

    def run(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_forever()
            if not self.queue.empty():
                queue_item = self.queue.get(timeout=3)
                self.queue_function(queue_item)
        finally:
            loop.close()
            self.queue.join()
            self.join()
            self.close()
