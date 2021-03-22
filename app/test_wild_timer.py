from unittest import TestCase
from wild_timer import ResettableTimer
import time

class TestResettableTimer(TestCase):
    ended = False

    def test_start(self):
        self.ended = False
        timer = ResettableTimer(interval=5, timeout=30,
                                function=self.has_triggered)
        timer.start()
        time.sleep(6)
        self.assertTrue(self.ended)

    def test_reset(self):
        self.ended = False
        timer = ResettableTimer(interval=5, timeout=30,
                                function=self.has_triggered)
        timer.start()
        time.sleep(4)
        timer.reset()
        self.assertFalse(self.ended)
        time.sleep(4)
        self.assertFalse(self.ended)
        time.sleep(2)
        self.assertTrue(self.ended)

    def test_timeout(self):
        self.ended = False
        timer = ResettableTimer(interval=5, timeout=10,
                                function=self.has_triggered)
        timer.start()
        time.sleep(4)
        timer.reset()
        time.sleep(4)
        timer.reset()
        time.sleep(2.01)
        self.assertTrue(self.ended)

    def has_triggered(self):
        self.ended = True
