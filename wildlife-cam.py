#!/usr/bin/python3

from picamera import PiCamera
from pathlib import Path
import RPi.GPIO as GPIO
from logzero import logger, logfile
import time
import configparser
import pysftp
import telepot
import requests
from multiprocessing import Process, Queue
import os

# Load Config File
config = configparser.ConfigParser()
config.read("/home/pi/WildlifeCam/WildlifeCam.ini")

# GPIO pin for the PIR sensor
PIR_GPIO_PIN = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_GPIO_PIN, GPIO.IN)


def handle_telegram_message(msg):
    logger.info("wildlife-cam: Got telegram message")

    chat_id = config['Telegram']['ChatId']
    message_chat_id = str(msg['chat']['id'])
    if message_chat_id != chat_id:
        logger.warning("wildlife-cam: Got telegram message from unknown chat id: %s", message_chat_id)
        return

    message_text = msg['text']
    if message_text.startswith('/snap'):
        logger.info("wildlife-cam: Got telegram command to snap a photo")
        snap_photo()


def snap_photo():
    logger.info("wildlife-cam: Capturing a photo")
    photo_dir_path = config['General']['PhotoDirPath']

    current_time = time.localtime()
    sub_folder_name = time.strftime("%Y-%m-%d", current_time)
    sub_folder_path = photo_dir_path + sub_folder_name + "/"
    Path(sub_folder_path).mkdir(parents=True, exist_ok=True)

    file_name = time.strftime("%Y-%m-%d-%H-%M-%S", current_time) + ".jpeg"
    file_path = sub_folder_path + file_name

    camera.resolution = (1024, 768)
    camera.capture(file_path)

    logger.info("wildlife-cam: Photo saved at %s", file_path)

    image_processing_queue.put(file_path)


def setup_logging():
    log_dir_path = config['General']['LogDirPath']
    logfile(log_dir_path + "wildlife-cam.log", maxBytes=1e6, backupCount=3)


def send_telegram_message(file_path):
    logger.info("wildlife-cam: Sending Message to Telegram.")
    telegram_api_key = config['Telegram']['ApiKey']
    telegram_chat_id = config['Telegram']['ChatId']

    url = "https://api.telegram.org/bot{api_key}/sendPhoto".format(api_key=telegram_api_key)
    payload = {'chat_id': telegram_chat_id}
    files = [('photo', ('wildlife.jpg', open(file_path, 'rb'), 'image/jpeg'))]
    response = requests.request("POST", url, data=payload, files=files, timeout=1.5)

    if response.status_code != 200:
        print("wildlife-cam: Sending Message to Telegram failed.")


def upload_to_sftp(file_path):
    logger.info("wildlife-cam: Upload Photo to SFTP.")
    sftp_host = config['SFTP']['IpAddress']
    sftp_port = int(config['SFTP']['Port'])
    sftp_username = config['SFTP']['Username']
    sftp_password = config['SFTP']['Password']
    sftp_dir = config['SFTP']['Directory']

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    srv = pysftp.Connection(host=sftp_host, port=sftp_port, username=sftp_username,
                            password=sftp_password, cnopts=cnopts)

    base_path, _ = os.path.split(file_path)
    _, sub_folder_name = os.path.split(base_path)

    with srv.cd(sftp_dir):
        if not srv.exists(sub_folder_name):
            srv.mkdir(sub_folder_name)
        with srv.cd(sub_folder_name):
            srv.put(file_path)

    srv.close()


class Worker(Process):
    def __init__(self, q, *args, **kwargs):
        self.q = q
        super().__init__(*args, **kwargs)

    def run(self):
        while True:
            if not self.q.empty():
                file_path = self.q.get(timeout=3)
                process_image(file_path)
                self.q.task_done()


def process_image(file_path):
    if config.has_section('Telegram'):
        send_telegram_message(file_path)

    if config.has_section('SFTP'):
        upload_to_sftp(file_path)


def handle_motion_detected(pir_sensor):
    logger.info("wildlife-cam: Motion detected.")
    snap_photo()


logger.info("wildlife-cam: Starting")
time.sleep(2)

camera = PiCamera()


if config.has_section('Telegram'):
    bot = telepot.Bot(config['Telegram']['ApiKey'])
    bot.message_loop(handle_telegram_message)

image_processing_queue = Queue()
image_processing_worker = Worker(image_processing_queue)
image_processing_worker.start()

try:
    logger.info("wildlife-cam: Ready and waiting for motion")
    GPIO.add_event_detect(PIR_GPIO_PIN, GPIO.RISING, callback=handle_motion_detected)
    while True:
        time.sleep(2)
except KeyboardInterrupt:
    logger.info("wildlife-cam: Stopping Wildlife Cam")
    camera.close()
    GPIO.cleanup()
    image_processing_worker.join()
