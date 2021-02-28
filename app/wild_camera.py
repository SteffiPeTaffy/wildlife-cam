import time

from picamera import PiCamera
from pathlib import Path
from datetime import datetime
from logzero import logger

from queue_worker import QueueItem, MediaType


class Camera(PiCamera):
    def __init__(self, photo_dir_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.photo_dir_path = photo_dir_path
        self.handlers = []
        self.started_recording = None
        self.current_video = None
        self.resolution = (1024, 768)

    def capture_photo(self):
        file_path = self.__get_file_path('.jpeg')

        self.capture(file_path)
        logger.info("wildlife-cam: Snapped a Photo %s", file_path)

        self.__call_handlers(QueueItem(MediaType.PHOTO, [file_path]))

    def __get_file_path(self, file_ending):
        current_time = datetime.utcnow()
        sub_folder_name = current_time.strftime("%Y-%m-%d")
        sub_folder_path = self.photo_dir_path + sub_folder_name + "/"
        Path(sub_folder_path).mkdir(parents=True, exist_ok=True)

        file_name = current_time.strftime("%Y-%m-%d-%H-%M-%S-%f")[:-3] + file_ending
        file_path = sub_folder_path + file_name
        return file_path

    def __call_handlers(self, item):
        for handler in self.handlers:
            handler(item)

    def add_camera_handler(self, handler):
        self.handlers.append(handler)

    def capture_series(self, size):
        series = []
        for i in range(size):
            file_path = self.__get_file_path('.jpeg')
            self.capture(file_path)
            series.append(file_path)

        self.__call_handlers(QueueItem(MediaType.SERIES, series))

    def record_clip(self, seconds):
        if self.started_recording:
            if self.started_recording + seconds < time.time():
                self.stop_recording()
                self.__call_handlers(QueueItem(MediaType.VIDEO, [self.current_video]))
                self.current_video = None
                self.started_recording = None
        else:
            file_path = self.__get_file_path('.mjpeg')
            self.start_recording(file_path)
            self.started_recording = time.time()
            self.current_video = file_path
