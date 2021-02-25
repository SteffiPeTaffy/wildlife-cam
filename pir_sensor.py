import RPi.GPIO as GPIO


class Sensor(GPIO):
    def __init__(self, config, *args, **kwargs):
        self.pin = int(config['Pin'])
        super().__init__(*args, **kwargs)

    def run(self):
        self.setmode(GPIO.BCM)
        self.setup(self.pin, GPIO.IN)

    def add_motion_detected_handler(self, handle_motion_detected):
        self.add_event_detect(self.pin, GPIO.RISING, callback=lambda pir: handle_motion_detected())
