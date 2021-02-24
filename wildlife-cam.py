#!/usr/bin/python3

import RPi.GPIO as GPIO
from logzero import logger, logfile
import time
import configparser
from telegram_updater import Telegram
from ftp_uploader import Uploader
import asyncio

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
time.sleep(2)

camera = Camera(config['General'])

if config.has_section('Telegram'):
    telegram = Telegram(config['Telegram'])
    camera.add_snap_handler(telegram.queue.put_nowait)

if config.has_section('SFTP'):
    ftp_uploader = Uploader(config['SFTP'])
    camera.add_snap_handler(ftp_uploader.queue.put_nowait)

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
