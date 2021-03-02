import os
import subprocess

import time
from multiprocessing import Process
from logzero import logger
from typing import List
from enum import Enum, auto


class MediaType(Enum):
    PHOTO = auto()
    VIDEO = auto()
    SERIES = auto()


class MediaItem:
    type: MediaType
    media: List[str]

    def __init__(self, media_type, media, caption):
        self.type = media_type
        self.media = media
        self.caption = caption


def convert_video(queue_item):
    file_path = queue_item.media[0]
    file_path_no_ending, _ = os.path.splitext(file_path)
    mp4_file_path = file_path_no_ending + '.mp4'
    command = "MP4Box -add {} {}".format(file_path, mp4_file_path)
    try:
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        queue_item.media = [mp4_file_path]
    except subprocess.CalledProcessError:
        logger.info("wildlife-cam: Failed to convert video clip to mp4")


class MediaWorker(Process):
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
                    if queue_item.type == MediaType.VIDEO:
                        convert_video(queue_item)
                    self.queue_function(queue_item)
                except Exception as e:
                    logger.exception(e)
