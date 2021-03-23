from unittest import TestCase
from wild_timer import ResettableTimer
import time


class TestResettableTimer(TestCase):
    ended = False

    def test_start(self):
        self.ended = False
        timer = ResettableTimer(interval=1, timeout=30,
                                function=self.has_triggered)
        timer.start()
        self.assertFalse(self.ended)
        time.sleep(1.1)
        self.assertTrue(self.ended)

    def test_reset(self):
        self.ended = False
        timer = ResettableTimer(interval=1, timeout=30,
                                function=self.has_triggered)
        timer.start()
        self.assertFalse(self.ended)
        time.sleep(0.8)
        timer.reset()
        self.assertFalse(self.ended)
        time.sleep(0.5)
        self.assertFalse(self.ended)
        time.sleep(0.6)
        self.assertTrue(self.ended)

    def test_timeout(self):
        self.ended = False
        timer = ResettableTimer(interval=1, timeout=5,
                                function=self.has_triggered)
        timer.start()
        time.sleep(0.8)
        timer.reset()
        time.sleep(0.8)
        timer.reset()
        time.sleep(3.5)
        self.assertTrue(self.ended)

    def test_not_reset_after_timeout_reached(self):
        self.ended = False
        timer = ResettableTimer(interval=1, timeout=3,
                                function=self.has_triggered)

        timer.start()
        time.sleep(0.8)
        timer.reset()
        time.sleep(0.8)
        timer.reset()
        time.sleep(0.8)
        timer.reset()
        time.sleep(0.8)
        self.assertTrue(self.ended)

    def has_triggered(self):
        self.ended = True
