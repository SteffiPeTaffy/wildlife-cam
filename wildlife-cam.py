#!/usr/bin/python3

import RPi.GPIO as GPIO
from logzero import logger, logfile
import time
import configparser

from queue_worker import Worker
from telegram_updater import Telegram
from ftp_uploader import Uploader
import asyncio
from multiprocessing import Queue

# Load Config File
from wild_camera import Camera

config = configparser.ConfigParser()
config.read("/home/pi/WildlifeCam/WildlifeCam.ini")

# GPIO pin for the PIR sensor
PIR_GPIO_PIN = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_GPIO_PIN, GPIO.IN)


def setup_logging():
    log_dir_path = config['General']['LogDirPath']
    logfile(log_dir_path + "wildlife-cam.log", maxBytes=1e6, backupCount=3)


def handle_motion_detected(pir_sensor):
    logger.info("wildlife-cam: Motion detected.")
    camera.snap_photo()


logger.info("wildlife-cam: Starting")

camera = Camera(config['General'])
camera.resolution = (1024, 768)
time.sleep(2)

if config.has_section('Telegram'):
    logger.info("wildlife-cam: Setting up Telegram")
    telegram = Telegram(config['Telegram'])
    telegram.add_command_handler("snap", camera.snap_photo)
    telegram.start_polling()

    telegram_queue = Queue()
    camera.add_snap_handler(telegram_queue.put_nowait)

    telegram_worker = Worker(telegram_queue, telegram.send_photo)
    telegram_worker.start()


if config.has_section('SFTP'):
    logger.info("wildlife-cam: Setting up FTP Upload")
    ftp_uploader = Uploader(config['SFTP'])

    ftp_queue = Queue()
    camera.add_snap_handler(ftp_queue.put_nowait)

    ftp_worker = Worker(ftp_queue, ftp_uploader.upload)
    ftp_worker.start()


logger.info("wildlife-cam: Ready and waiting for motion")
GPIO.add_event_detect(PIR_GPIO_PIN, GPIO.RISING, callback=handle_motion_detected)

loop = asyncio.get_event_loop()
try:
    loop.run_forever()
finally:
    logger.info("wildlife-cam: Stopping Wildlife Cam")
    loop.close()
    camera.close()
    GPIO.cleanup()
