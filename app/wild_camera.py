from picamera import PiCamera
from pathlib import Path
from datetime import datetime
from logzero import logger


class Camera(PiCamera):
    def __init__(self, camera_config, *args, **kwargs):
        self.photo_dir_path = camera_config['PhotoDirPath']
        self.handlers = []
        super().__init__(*args, **kwargs)

    def snap_photo(self):
        current_time = datetime.utcnow()
        sub_folder_name = current_time.strftime("%Y-%m-%d")
        sub_folder_path = self.photo_dir_path + sub_folder_name + "/"
        Path(sub_folder_path).mkdir(parents=True, exist_ok=True)

        file_name = current_time.strftime("%Y-%m-%d-%H-%M-%S-%f")[:-3] + ".jpeg"
        file_path = sub_folder_path + file_name

        self.capture(file_path)
        logger.info("wildlife-cam: Snapped a Photo %s", file_path)

        for handler in self.handlers:
            handler(file_path)

    def add_snap_handler(self, handler):
        self.handlers.append(handler)
