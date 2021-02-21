from gpiozero import MotionSensor
from picamera import PiCamera
import time
import sys

# Sys Args
PHOTO_PATH = sys.argv[0]

# GPIO pin for the PIR sensor
PIR_GPIO_PIN = 4
WAIT_TIME = 2

pir = MotionSensor(PIR_GPIO_PIN)
camera = PiCamera()


def generate_file_name():
    return PHOTO_PATH + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + ".jpeg"


def snap_photo():
    camera.resolution = (1024, 768)
    camera.capture(generate_file_name())


print("wildlife-cam: Starting")
pir.wait_for_no_motion()
try:
    while True:
        print("wildlife-cam: Ready and waiting for motion")
        pir.wait_for_motion()
        print("wildlife-cam: Motion detected.")
        snap_photo()
        time.sleep(WAIT_TIME)
except KeyboardInterrupt:
    print("wildlife-cam: Stopping Wildlife Cam")
    camera.close()
