import RPi.GPIO as GPIO
import time

# GPIO pin for the PIR sensor
PIR_GPIO_PIN = 2

# setup GPIO pin for the PIR (motion) sensor
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_GPIO_PIN, GPIO.IN)

# time to wait after taking a photo in seconds
WAIT_TIME = 2


#  take a photo when motion is detected
def motion_detected(pir_sensor):
    print("wildlife-cam: Motion detected.")


# do the loop
while True:
    try:
        print("wildlife-cam: Waiting for motion.")
        GPIO.wait_for_edge(PIR_GPIO_PIN, GPIO.RISING)
        motion_detected(PIR_GPIO_PIN)
        print("wildlife-cam: Sleeping for " + str(WAIT_TIME) + " seconds.")
        time.sleep(WAIT_TIME)
    except KeyboardInterrupt:
        print("wildlife-cam: Stopping due to keyboard interrupt.")
        GPIO.cleanup()
        break
