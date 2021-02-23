#!/usr/bin/python3

from picamera import PiCamera
from pathlib import Path
import RPi.GPIO as GPIO
from logzero import logger, logfile
import time
import configparser
import pysftp
import telepot

# Load Config File
config = configparser.ConfigParser()
config.read("/home/pi/WildlifeCam/WildlifeCam.ini")

WAIT_TIME = 2

# GPIO pin for the PIR sensor
PIR_GPIO_PIN = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_GPIO_PIN, GPIO.IN)

camera = PiCamera()


def handle_telegram_message(msg):
    logger.debug("wildlife-cam: Got telegram message: %s", msg)

    chat_id = config['Telegram']['ChatId']

    message_chat_id = str(msg['chat']['id'])
    if message_chat_id != chat_id:
        logger.warning("wildlife-cam: Got telegram message from unknown chat id: %s", message_chat_id)
        return

    message_text = msg['text']
    if message_text.startswith('/snap'):
        _, file_path = snap_photo()
        send_telegram_message(file_path)


def snap_photo():
    photo_dir_path = config['General']['PhotoDirPath']

    current_time = time.localtime()
    sub_folder_name = time.strftime("%Y-%m-%d", current_time)
    sub_folder_path = photo_dir_path + sub_folder_name + "/"
    Path(sub_folder_path).mkdir(parents=True, exist_ok=True)

    file_name = time.strftime("%Y-%m-%d-%H-%M-%S", current_time) + ".jpeg"
    file_path = sub_folder_path + file_name

    camera.resolution = (1024, 768)
    camera.capture(file_path)

    return [sub_folder_name, file_path]


def setup_logging():
    log_dir_path = config['General']['LogDirPath']
    logfile(log_dir_path + "wildlife-cam.log", maxBytes=1e6, backupCount=3)


def send_telegram_message(file_path):
    logger.info("wildlife-cam: Sending Message to Telegram.")
    chat_id = config['Telegram']['ChatId']
    bot.sendPhoto(chat_id, photo=open(file_path, 'rb'))


def upload_to_sftp(sub_folder_name, file_path):
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

    with srv.cd(sftp_dir):
        if not srv.exists(sub_folder_name):
            srv.mkdir(sub_folder_name)
        with srv.cd(sub_folder_name):
            srv.put(file_path)

    srv.close()


def handle_motion_detected(pir_sensor):
    logger.info("wildlife-cam: Motion detected.")

    sub_folder_name, file_path = snap_photo()

    if config.has_section('Telegram'):
        send_telegram_message(file_path)

    if config.has_section('SFTP'):
        upload_to_sftp(sub_folder_name, file_path)


logger.info("wildlife-cam: Starting")
time.sleep(2)
if config.has_section('Telegram'):
    bot = telepot.Bot(config['Telegram']['ApiKey'])
    bot.message_loop(handle_telegram_message)
try:
    logger.info("wildlife-cam: Ready and waiting for motion")
    GPIO.add_event_detect(PIR_GPIO_PIN, GPIO.RISING, callback=handle_motion_detected)
    while True:
        time.sleep(WAIT_TIME)
except KeyboardInterrupt:
    logger.info("wildlife-cam: Stopping Wildlife Cam")
    camera.close()
    GPIO.cleanup()
