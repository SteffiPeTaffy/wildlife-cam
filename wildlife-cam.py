from picamera import PiCamera
from pathlib import Path
import RPi.GPIO as GPIO
import time
import sys
import requests
import configparser
import pysftp

# Sys Args
CONFIG_FILE_PATH = sys.argv[1]
config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)

WAIT_TIME = 2

# GPIO pin for the PIR sensor
PIR_GPIO_PIN = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_GPIO_PIN, GPIO.IN)

camera = PiCamera()


def generate_file_name():
    return photo_dir_path + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + ".jpeg"


def snap_photo(file_path):
    camera.resolution = (1024, 768)
    camera.capture(file_path)


def send_telegram_message(file_path):
    print("wildlife-cam: Sending Message to Telegram.")
    telegram_api_key = config['Telegram']['ApiKey']
    telegram_chat_id = config['Telegram']['ChatId']

    url = "https://api.telegram.org/bot{api_key}/sendPhoto".format(api_key=telegram_api_key)
    payload = {'chat_id': telegram_chat_id}
    files = [('photo', ('wildlife.jpg', open(file_path, 'rb'), 'image/jpeg'))]
    response = requests.request("POST", url, data=payload, files=files, timeout=1.5)

    if response.status_code != 200:
        print("wildlife-cam: Sending Message to Telegram failed.")


def upload_to_sftp(file_name):
    print("wildlife-cam: Upload Photo to SFTP.")
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
        srv.put(file_name)

    srv.close()


def handle_motion_detected(pir_sensor):
    print("wildlife-cam: Motion detected.")
    photo_dir_path = config['General']['PhotoDirPath']

    folder_path = photo_dir_path + time.strftime("%Y-%m-%d", time.localtime())
    Path(folder_path).mkdir(parents=True, exist_ok=True)

    file_name = time.strftime("%H-%M-%S", time.localtime()) + ".jpeg"
    file_path = folder_path + "/" + file_name
    snap_photo(file_path)

    if config.has_section('Telegram'):
        send_telegram_message(file_path)

    if config.has_section('SFTP'):
        upload_to_sftp(file_path)


print("wildlife-cam: Starting")
time.sleep(2)
try:
    print("wildlife-cam: Ready and waiting for motion")
    GPIO.add_event_detect(PIR_GPIO_PIN, GPIO.RISING, callback=handle_motion_detected)
    while True:
        time.sleep(WAIT_TIME)
except KeyboardInterrupt:
    print("wildlife-cam: Stopping Wildlife Cam")
    camera.close()
    GPIO.cleanup()
