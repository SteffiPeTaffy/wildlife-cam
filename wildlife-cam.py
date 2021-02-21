from gpiozero import MotionSensor
from picamera import PiCamera
from pprint import pprint
import time
import sys
import requests
import configparser

# Sys Args
CONFIG_FILE_PATH = sys.argv[1]
config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)

# GPIO pin for the PIR sensor
PIR_GPIO_PIN = 4
WAIT_TIME = 2

pir = MotionSensor(PIR_GPIO_PIN)
camera = PiCamera()


def generate_file_name():
    photo_dir_path = config['General']['PhotoDirPath']
    return photo_dir_path + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + ".jpeg"


def snap_photo(file_name):
    camera.resolution = (1024, 768)
    camera.capture(file_name)


def send_telegram_message(file_name):
    print("wildlife-cam: Sending Message to Telegram.")
    telegram_api_key = config['Telegram']['ApiKey']
    telegram_chat_id = config['Telegram']['ChatId']

    files = {'photo': open(file_name, 'rb'), 'chat_id': telegram_chat_id}
    response = requests.post("https://api.telegram.org/bot{api_key}/sendPhoto".format(api_key=telegram_api_key),
                             files=files, timeout=2)

    if response.status_code != 200:
        print("wildlife-cam: Sending Message to Telegram failed.")
        pprint(response.json())


def handle_motion_detected():
    print("wildlife-cam: Motion detected.")

    file_name = generate_file_name()
    snap_photo(file_name)

    if config.has_section('Telegram'):
        send_telegram_message(file_name)


print("wildlife-cam: Starting")
pir.wait_for_no_motion()
try:
    while True:
        print("wildlife-cam: Ready and waiting for motion")
        pir.wait_for_motion()
        handle_motion_detected()
        time.sleep(WAIT_TIME)
except KeyboardInterrupt:
    print("wildlife-cam: Stopping Wildlife Cam")
    camera.close()
