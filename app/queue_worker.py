import time
from multiprocessing import Process
from logzero import logger
from typing import List
from enum import Enum, auto


class MediaType(Enum):
    PHOTO = auto()
    VIDEO = auto()
    SERIES = auto()


class QueueItem:
    type: MediaType
    media: List[str]

    def __init__(self, media_type, media):
        self.type = media_type
        self.media = media


class Worker(Process):
    def __init__(self, queue, queue_function, *args, **kwargs):
        self.queue = queue
        self.queue_function = queue_function
        super().__init__(*args, **kwargs)

    def run(self):
        while True:
            time.sleep(1.5)
            if not self.queue.empty():
                queue_item = self.queue.get(timeout=3)
                try:
                    self.queue_function(queue_item)
                except Exception as e:
                    logger.exception(e)
