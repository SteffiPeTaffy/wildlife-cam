#!/usr/bin/python3

from logzero import logger, logfile
import time
import configparser
from pir_sensor import Sensor
from queue_worker import Worker
from telegram_updater import Telegram
from ftp_uploader import Uploader
import asyncio
from multiprocessing import Queue

# Load Config File
from wild_camera import Camera

logger.info("wildlife-cam: Starting")

# get config file
config = configparser.ConfigParser()
config.read("/home/pi/WildlifeCam/WildlifeCam.ini")

# Setup logging
log_dir_path = config['General']['LogDirPath']
logfile(log_dir_path + "wildlife-cam.log", maxBytes=1e6, backupCount=3)

# Setup Camera
camera = Camera(config['General'])
camera.resolution = (1024, 768)
time.sleep(2)

# Setup Telegram if wanted
if config.has_section('Telegram'):
    logger.info("wildlife-cam: Setting up Telegram")
    telegram = Telegram(config['Telegram'])
    telegram.add_command_handler("snap", camera.snap_photo)
    telegram.start_polling()

    telegram_queue = Queue()
    camera.add_snap_handler(telegram_queue.put_nowait)

    telegram_worker = Worker(telegram_queue, telegram.send_photo)
    telegram_worker.start()

# Setup FTP Upload if wanted
if config.has_section('SFTP'):
    logger.info("wildlife-cam: Setting up FTP Upload")
    ftp_uploader = Uploader(config['SFTP'])

    ftp_queue = Queue()
    camera.add_snap_handler(ftp_queue.put_nowait)

    ftp_worker = Worker(ftp_queue, ftp_uploader.upload)
    ftp_worker.start()

# Setup PIR sensor
pir_sensor = Sensor(config['General'])
pir_sensor.add_motion_detected_handler(camera.snap_photo)

loop = asyncio.get_event_loop()
try:
    logger.info("wildlife-cam: Ready and waiting for motion")
    loop.run_forever()
finally:
    logger.info("wildlife-cam: Stopping Wildlife Cam")
    loop.close()
    camera.close()
    pir_sensor.cleanup()
