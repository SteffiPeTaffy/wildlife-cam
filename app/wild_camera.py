from picamera import PiCamera, PiCameraRuntimeError
from pathlib import Path
from datetime import datetime
from logzero import logger
from threading import Timer
from enum import Enum, auto

from queue_worker import MediaItem, MediaType


class CameraStatus(Enum):
    RUNNING = auto()
    PAUSED = auto()
    STOPPED = auto()


class Camera(PiCamera):
    def __init__(self, photo_dir_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.photo_dir_path = photo_dir_path
        self.handlers = []
        self.resolution = (1280, 720)
        self.framerate = 24
        self.status = CameraStatus.STOPPED
        self.pause_timer = None

    def capture_photo(self, caption=''):
        file_path = self.__capture_photo()

        logger.info("wildlife-cam: Snapped a photo")
        self.__call_handlers(MediaItem(media_type=MediaType.PHOTO, media=[file_path], caption=caption))

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

    def capture_series(self, size=3, caption=''):
        series = []
        for i in range(size):
            file_path = self.__capture_photo()
            series.append(file_path)

        logger.info("wildlife-cam: Snapped a Series of photos")
        self.__call_handlers(MediaItem(media_type=MediaType.SERIES, media=series, caption=caption))

    def __stop_clip(self, file_path, caption):
        if self.recording and file_path:
            self.stop_recording()
            logger.info("wildlife-cam: Recorded a video clip")
            self.__call_handlers(MediaItem(media_type=MediaType.VIDEO, media=[file_path], caption=caption))

    def start_clip(self, seconds=5, caption=''):
        if not self.recording:
            video_file_path = self.__get_file_path('.h264')
            self.start_recording(video_file_path, resize=(480, 320))
            logger.info("wildlife-cam: Started recording a video clip")
            t = Timer(seconds, self.__stop_clip, **{'file_path': video_file_path, 'caption': caption})
            t.start()

    def start(self):
        if self.pause_timer:
            self.pause_timer.cancel()
        if self.status != CameraStatus.RUNNING:
            self.status = CameraStatus.RUNNING
            self.capture_photo('Wildlife Cam is up and ready to go!')

    def stop(self):
        if self.pause_timer:
            self.pause_timer.cancel()
        if self.status != CameraStatus.STOPPED:
            self.status = CameraStatus.STOPPED
            self.capture_photo('Wildlife Cam is stopped now!')

    def pause(self, seconds=60):
        if type(seconds) != int or type(seconds) != float:
            seconds = 60

        if self.status != CameraStatus.PAUSED:
            self.status = CameraStatus.PAUSED
            self.capture_photo('Wildlife Cam is paused for {} seconds!'.format(seconds))
            self.pause_timer = Timer(seconds, self.start)
            self.pause_timer.start()
