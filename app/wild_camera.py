import time

from picamera import PiCamera, PiCameraRuntimeError
from pathlib import Path
from datetime import datetime
from logzero import logger
from threading import Timer

from queue_worker import QueueItem, MediaType


class Camera(PiCamera):
    def __init__(self, photo_dir_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.photo_dir_path = photo_dir_path
        self.handlers = []
        self.current_video_file_path = None
        self.resolution = (1280, 720)

    def capture_photo(self):
        file_path = self.__capture_photo()

        logger.info("wildlife-cam: Snapped a photo")
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

    def __capture_photo(self):
        file_path = self.__get_file_path('.jpeg')
        self.capture(file_path, use_video_port=self.__is_recording())
        return file_path

    def capture_series(self, size):
        series = []
        for i in range(size):
            file_path = self.__capture_photo()
            series.append(file_path)

        logger.info("wildlife-cam: Snapped a Series of photos")
        self.__call_handlers(QueueItem(MediaType.SERIES, series))

    def __is_recording(self):
        if not self.current_video_file_path:
            return False
        return True

    def stop_clip(self):
        if self.__is_recording():
            video_file_path = self.current_video_file_path
            self.stop_recording()
            self.current_video_file_path = None

            logger.info("wildlife-cam: Recorded a video clip")
            self.__call_handlers(QueueItem(MediaType.VIDEO, [video_file_path]))

    def start_clip(self, seconds):
        if not self.__is_recording():
            video_file_path = self.__get_file_path('.mjpeg')
            self.current_video_file_path = video_file_path
            self.start_recording(video_file_path)
            t = Timer(seconds, self.stop_clip)
            t.start()
