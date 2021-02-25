#!/usr/bin/python3

import time
import configparser
import RPi.GPIO as GPIO
from logzero import logger, logfile
from queue_worker import Worker
from telegram_updater import Telegram
from ftp_uploader import Uploader
from multiprocessing import Queue
from wild_camera import Camera


def motion_detected(pir):
    logger.info("wildlife-cam: Motion detected")
    camera.snap_photo()
    count = 0
    while count < 4:
        time.sleep(0.2)
        camera.snap_photo()
        count += 1


# Load Config File
logger.info("wildlife-cam: Starting")

# get config file
config = configparser.ConfigParser()
config.read("/home/pi/WildlifeCam/WildlifeCam.ini")

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
pir_sensor_pin = int(config['PirSensor']['Pin'])
GPIO.setmode(GPIO.BCM)
GPIO.setup(pir_sensor_pin, GPIO.IN)
GPIO.add_event_detect(pir_sensor_pin, GPIO.RISING, motion_detected)

try:
    logger.info("wildlife-cam: Ready and waiting for motion")
    while True:
        time.sleep(100)
finally:
    logger.info("wildlife-cam: Stopping Wildlife Cam")
    camera.close()
    GPIO.cleanup()
