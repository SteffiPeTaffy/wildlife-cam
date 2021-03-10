#!/usr/bin/env python3

from logzero import logger, logfile

from wild_config import WildlifeCamConfig
from queue_worker import MediaWorker
from telegram_updater import Telegram
from ftp_uploader import Uploader
from multiprocessing import Queue
from wild_camera import MotionCamera
from signal import pause

logger.info("wildlife-cam: Starting")

# Load Config File
config = WildlifeCamConfig('/home/pi/WildlifeCam/WildlifeCam.ini')

# Setup Camera
photo_dir_path = config.get('General', 'PhotoDirPath')
pir_sensor_pin = config.getint('PirSensor', 'Pin')
motion_camera = MotionCamera(photo_dir_path, pir_sensor_pin)

# Setup Telegram if wanted
if config.has_section('Telegram'):
    logger.info("wildlife-cam: Setting up Telegram")
    api_token = config.get('Telegram', 'ApiKey')
    allowed_chat_id = config.getint('Telegram', 'ChatId')

    telegram = Telegram(api_token, allowed_chat_id)
    telegram.add_command_handler("snap", lambda: motion_camera.capture_photo(caption='Here\'s your photo!'))
    telegram.add_command_handler("clip", lambda: motion_camera.start_clip(caption='Here\'s your clip!'))

    telegram.add_command_handler_with_arg("pause",
                                          lambda seconds=60: telegram.send_message(
                                              message="Wildlife Cam is paused for {} seconds!".format(
                                                  motion_camera.pause(seconds=seconds))))

    telegram.add_command_handler("start",
                                 lambda: [telegram.send_message(message='Starting Wildlife Cam'), motion_camera.start()])

    telegram.add_command_handler("stop",
                                 lambda: [motion_camera.stop(), telegram.send_message(message="Wildlife Cam is stopped!")])

    telegram.add_command_handler("status",
                                 lambda: telegram.send_message(
                                     message="Wildlife Cam is {}".format(motion_camera.get_status_message())))

    telegram.start_polling()

    telegram_queue = Queue()
    motion_camera.add_camera_handler(telegram_queue.put_nowait)

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
    motion_camera.add_camera_handler(ftp_queue.put_nowait)

    ftp_worker = MediaWorker(ftp_queue, ftp_uploader.upload, 1)
    ftp_worker.start()

motion_camera.start()
pause()
