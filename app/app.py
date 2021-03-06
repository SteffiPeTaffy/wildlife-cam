#!/usr/bin/env python3

import time
from logzero import logger, logfile

from wild_config import WildlifeCamConfig
from queue_worker import MediaWorker
from telegram_updater import Telegram
from ftp_uploader import Uploader
from multiprocessing import Queue
from wild_camera import Camera, CameraStatus
from gpiozero import MotionSensor
from signal import pause


def handle_motion():
    if camera.status == CameraStatus.RUNNING:
        logger.info("wildlife-cam: Motion detected")
        camera.start_clip(5, 'Motion detected!')
        camera.capture_series(3, 'Motion detected!')


logger.info("wildlife-cam: Starting")

# Load Config File
config = WildlifeCamConfig('/home/pi/WildlifeCam/WildlifeCam.ini')

# Setup Camera
photo_dir_path = config.get('General', 'PhotoDirPath')
camera = Camera(photo_dir_path)
time.sleep(2)

# Setup Telegram if wanted
if config.has_section('Telegram'):
    logger.info("wildlife-cam: Setting up Telegram")
    api_token = config.get('Telegram', 'ApiKey')
    allowed_chat_id = config.getint('Telegram', 'ChatId')

    telegram = Telegram(api_token, allowed_chat_id)
    telegram.add_command_handler("snap", lambda: camera.capture_photo(caption='Here\'s your photo!'))
    telegram.add_command_handler("clip", lambda: camera.start_clip(caption='Here\'s your clip!'))
    telegram.add_command_handler("pause", camera.pause)
    telegram.add_command_handler("start", camera.start)
    telegram.add_command_handler("stop", camera.stop)
    telegram.start_polling()

    telegram_queue = Queue()
    camera.add_camera_handler(telegram_queue.put_nowait)

    telegram_worker = MediaWorker(telegram_queue, telegram.send_media_message, 3)
    telegram_worker.start()

# Setup FTP Upload if wanted
if config.has_section('SFTP'):
    logger.info("wildlife-cam: Setting up FTP Upload")
    sftp_host = config.get('SFTP', 'IpAddress')
    sftp_port = config.getint('SFTP', 'Port')
    sftp_username = config.get('SFTP', 'Username')
    sftp_password = config.get('SFTP', 'Password')
    sftp_dir = config.get('SFTP', 'Directory')

    ftp_uploader = Uploader(sftp_host, sftp_port, sftp_username, sftp_password, sftp_dir)

    ftp_queue = Queue()
    camera.add_camera_handler(ftp_queue.put_nowait)

    ftp_worker = MediaWorker(ftp_queue, ftp_uploader.upload, 1)
    ftp_worker.start()

# Setup PIR sensor
pir_sensor_pin = config.getint('PirSensor', 'Pin')
pir_sensor = MotionSensor(pir_sensor_pin)

try:
    pir_sensor.wait_for_no_motion(2)
    logger.info("wildlife-cam: Ready and waiting for motion")
    camera.start()
    pir_sensor.when_motion = handle_motion
    pause()

finally:
    logger.info("wildlife-cam: Stopping Wildlife Cam")
    camera.stop()
    camera.close()
