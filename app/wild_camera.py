import os
import subprocess

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
        self.resolution = (1280, 720)
        self.framerate = 24

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
        self.capture(file_path, use_video_port=self.recording, resize=(1280, 720))
        return file_path

    def capture_series(self, size):
        series = []
        for i in range(size):
            file_path = self.__capture_photo()
            series.append(file_path)

        logger.info("wildlife-cam: Snapped a Series of photos")
        self.__call_handlers(QueueItem(MediaType.SERIES, series))

    def stop_clip(self, *args, **kwargs):
        if self.recording:
            self.stop_recording()
            file_path = args[0]
            file_path_no_ending, _ = os.path.splitext(file_path)
            mp4_file_path = file_path_no_ending + '.mp4'
            command = "MP4Box -add {} {}".format(file_path, mp4_file_path)
            try:
                subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
                logger.info("wildlife-cam: Recorded a video clip")
                self.__call_handlers(QueueItem(MediaType.VIDEO, [mp4_file_path]))
            except subprocess.CalledProcessError:
                logger.info("wildlife-cam: Failed to convert video clip to mp4")

    def start_clip(self, seconds):
        if not self.recording:
            video_file_path = self.__get_file_path('.h264')
            self.start_recording(video_file_path, resize=(480, 320))
            logger.info("wildlife-cam: Started recording a video clip")
            t = Timer(seconds, self.stop_clip, [video_file_path, ])
            t.start()
