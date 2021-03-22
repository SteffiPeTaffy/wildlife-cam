from picamera import PiCamera, PiCameraRuntimeError
from pathlib import Path
from datetime import datetime
from logzero import logger
from threading import Timer
from enum import Enum, auto
from gpiozero import MotionSensor

from wild_timer import RemainingTimer, ResettableTimer
from queue_worker import MediaItem, MediaType


class CameraStatus(Enum):
    RUNNING = auto()
    PAUSED = auto()
    STOPPED = auto()


class MotionCamera(PiCamera):
    def __init__(self, photo_dir_path, pir_sensor_pin, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._photo_dir_path = photo_dir_path
        self._handlers = []
        self._status = CameraStatus.STOPPED
        self.resolution = (1280, 720)
        self.framerate = 24
        self._pause_timer = None
        self._motion_timer = None
        self._pir_sensor = MotionSensor(pir_sensor_pin)

    def __handle_motion(self):
        logger.info("wildlife-cam: Motion started detected")
        self.__start_motion_clip(caption='Motion detected!')
        self._motion_timer.reset()
        self.capture_series(3, 'Motion detected!')

    def __handle_no_motion(self):
        logger.info("wildlife-cam: Motion stopped detected")
        # self._motion_timer.trigger()

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

    def __capture_photo(self):
        file_path = self.__get_file_path('.jpeg')
        self.capture(file_path, use_video_port=self.recording, resize=(1280, 720))
        return file_path

    def __stop_clip(self, file_path, caption):
        if self.recording:
            logger.info("wildlife-cam: Recorded a video clip")
            self.stop_recording()
            self.__call_handlers(MediaItem(media_type=MediaType.VIDEO, media=[file_path], caption=caption))

    def start_clip(self, seconds=5, caption=''):
        if not self.recording:
            logger.info("wildlife-cam: Started recording a video clip")
            video_file_path = self.__get_file_path('.h264')
            self.start_recording(video_file_path, resize=(480, 320))
            Timer(seconds, lambda: self.__stop_clip(file_path=video_file_path, caption=caption)).start()

    def __start_motion_clip(self, caption=''):
        if not self.recording:
            logger.info("wildlife-cam: Started recording a video clip")
            video_file_path = self.__get_file_path('.h264')
            self.start_recording(video_file_path, resize=(480, 320))
            self._motion_timer = ResettableTimer(interval=5, timeout=30,
                                                 function=lambda: self.__stop_clip(file_path=video_file_path,
                                                                                   caption=caption))
            self._motion_timer.start()

    def __cancel_timers(self):
        if self._pause_timer and self._pause_timer.is_alive():
            self._pause_timer.cancel()
        if self._motion_timer and self._motion_timer.is_alive():
            self._motion_timer.cancel()

    def capture_photo(self, caption=''):
        file_path = self.__capture_photo()

        logger.info("wildlife-cam: Snapped a photo")
        self.__call_handlers(MediaItem(media_type=MediaType.PHOTO, media=[file_path], caption=caption))

    def capture_series(self, size=3, caption=''):
        series = []
        for i in range(size):
            file_path = self.__capture_photo()
            series.append(file_path)

        logger.info("wildlife-cam: Snapped a Series of photos")
        self.__call_handlers(MediaItem(media_type=MediaType.SERIES, media=series, caption=caption))

    def add_camera_handler(self, handler):
        self._handlers.append(handler)

    def start(self):
        self.__cancel_timers()
        self._status = CameraStatus.RUNNING
        logger.info("wildlife-cam: Wildlife Cam is ready and waiting for motion")
        self.capture_photo('Wildlife Cam is started and ready to go!')
        self._pir_sensor.when_motion = self.__handle_motion
        self._pir_sensor.when_no_motion = self.__handle_no_motion

    def stop(self):
        self._pir_sensor.when_motion = None
        self._pir_sensor.when_no_motion = None
        self.__cancel_timers()
        self._status = CameraStatus.STOPPED
        logger.info("wildlife-cam: Wildlife Cam is stopped")

    def pause(self, seconds=60):
        self._pir_sensor.when_motion = None
        self._pir_sensor.when_no_motion = None
        self.__cancel_timers()
        self._status = CameraStatus.PAUSED

        if not seconds or int(seconds) < 0 or int(seconds) > 60 * 5:  # don't pause longer than 5 minutes
            seconds = 60
        self._pause_timer = RemainingTimer(int(seconds), self.start)
        self._pause_timer.start_timer()
        logger.info("wildlife-cam: Wildlife Cam is paused for {} seconds".format(seconds))

        return seconds

    def get_status_message(self):
        if self._status == CameraStatus.RUNNING:
            return 'up and running'
        if self._status == CameraStatus.STOPPED:
            return 'stopped'
        if self._status == CameraStatus.PAUSED:
            return 'paused and has {} seconds left until starting again'.format(int(self._pause_timer.remaining()))
