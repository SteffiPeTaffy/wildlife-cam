from picamera import PiCamera, PiCameraRuntimeError
from pathlib import Path
from datetime import datetime
from logzero import logger
from threading import Timer
from enum import Enum, auto

from wild_timer import RemainingTimer
from queue_worker import MediaItem, MediaType


class CameraStatus(Enum):
    RUNNING = auto()
    PAUSED = auto()
    STOPPED = auto()


class Camera(PiCamera):
    def __init__(self, photo_dir_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._photo_dir_path = photo_dir_path
        self._handlers = []
        self.resolution = (1280, 720)
        self.framerate = 24
        self.status = CameraStatus.STOPPED
        self._pause_timer = None

    def capture_photo(self, caption=''):
        file_path = self.__capture_photo()

        logger.info("wildlife-cam: Snapped a photo")
        self.__call_handlers(MediaItem(media_type=MediaType.PHOTO, media=[file_path], caption=caption))

    def __get_file_path(self, file_ending):
        current_time = datetime.utcnow()
        sub_folder_name = current_time.strftime("%Y-%m-%d")
        sub_folder_path = self._photo_dir_path + sub_folder_name + "/"
        Path(sub_folder_path).mkdir(parents=True, exist_ok=True)

        file_name = current_time.strftime("%Y-%m-%d-%H-%M-%S-%f")[:-3] + file_ending
        file_path = sub_folder_path + file_name
        return file_path

    def __call_handlers(self, item):
        for handler in self._handlers:
            handler(item)

    def add_camera_handler(self, handler):
        self._handlers.append(handler)

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
            t = Timer(seconds, self.__stop_clip, kwargs=({'file_path': video_file_path, 'caption': caption}))
            t.start()

    def __cancel_pause_timer(self):
        if self._pause_timer and self._pause_timer.is_alive():
            self._pause_timer.cancel()

    def start(self):
        self.__cancel_pause_timer()
        self.status = CameraStatus.RUNNING
        self.capture_photo('Wildlife Cam is started and ready to go!')
        logger.info("wildlife-cam: Wildlife Cam is started")

    def stop(self):
        self.__cancel_pause_timer()
        self.status = CameraStatus.STOPPED
        logger.info("wildlife-cam: Wildlife Cam is stopped")

    def pause(self, seconds=60):
        self.__cancel_pause_timer()

        if not seconds or int(seconds) < 0 or int(seconds) > 60 * 5:  # don't pause longer than 5 minutes
            seconds = 60

        self.status = CameraStatus.PAUSED
        self._pause_timer = RemainingTimer(int(seconds), self.start)
        self._pause_timer.start_timer()
        logger.info("wildlife-cam: Wildlife Cam is paused for {} seconds".format(seconds))

        return seconds

    def get_status_message(self):
        if self.status == CameraStatus.RUNNING:
            return 'up and running'
        if self.status == CameraStatus.STOPPED:
            return 'stopped'
        if self.status == CameraStatus.PAUSED:
            return 'paused and has {} seconds left until starting again'.format(int(self._pause_timer.remaining()))
