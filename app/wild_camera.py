from picamera import PiCamera
from pathlib import Path
from datetime import datetime
from logzero import logger

from app.queue_worker import QueueItem


class Camera(PiCamera):
    def __init__(self, photo_dir_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.photo_dir_path = photo_dir_path
        self.handlers = []
        self.current_series = []
        self.current_video = None
        self.resolution = (1024, 768)

    def snap_photo(self):
        file_path = self.__get_file_path()

        self.capture(file_path)
        logger.info("wildlife-cam: Snapped a Photo %s", file_path)

        item = QueueItem('photo', [file_path])
        for handler in self.handlers:
            handler(item)

    def __get_file_path(self, file_ending):
        current_time = datetime.utcnow()
        sub_folder_name = current_time.strftime("%Y-%m-%d")
        sub_folder_path = self.photo_dir_path + sub_folder_name + "/"
        Path(sub_folder_path).mkdir(parents=True, exist_ok=True)

        file_name = current_time.strftime("%Y-%m-%d-%H-%M-%S-%f")[:-3] + file_ending
        file_path = sub_folder_path + file_name
        return file_path

    def add_camera_handler(self, handler):
        self.handlers.append(handler)

    def start_series(self):
        self.current_series = []

    def snap_series(self):
        file_path = self.__get_file_path('.jpeg')
        self.capture(file_path)
        self.current_series.append(file_path)

    def stop_series(self):
        item = QueueItem('series', self.current_series)
        for handler in self.handlers:
            handler(item)

    def start_video(self):
        file_path = self.__get_file_path('.h264')
        self.start_recording(file_path)
        self.current_video = file_path

    def stop_video(self):
        item = QueueItem('video', [self.current_video])
        for handler in self.handlers:
            handler(item)
