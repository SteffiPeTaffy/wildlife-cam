import RPi.GPIO as GPIO
import time

# GPIO pin for the PIR sensor
PIR_GPIO_PIN = 2

# setup GPIO pin for the PIR (motion) sensor
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_GPIO_PIN, GPIO.IN)

# time to wait after taking a photo in seconds
WAIT_TIME = 2

print(GPIO.RPI_INFO)


#  take a photo when motion is detected
def motion_detected(pir_sensor):
    print("wildlife-cam: Motion detected.")


time.sleep(2)
print("wildlife-cam: Ready and waiting for motion.")
try:
    GPIO.add_event_detect(PIR_GPIO_PIN, GPIO.RISING, callback=motion_detected)
    while True:
        time.sleep(WAIT_TIME)
except KeyboardInterrupt:
    print("wildlife-cam: Stopping due to keyboard interrupt.")
    GPIO.cleanup()
