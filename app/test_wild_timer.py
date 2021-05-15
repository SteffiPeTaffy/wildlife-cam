from unittest import TestCase
from wild_timer import ResettableTimer
import time


class TestResettableTimer(TestCase):

    def setUp(self):
        self.ended = False
        self.timer = ResettableTimer(interval=1, timeout=3,
                                     function=self.has_triggered)

    def test_start(self):
        self.timer.start()
        self.assertFalse(self.ended)
        time.sleep(1.1)
        self.assertTrue(self.ended)

    def test_reset(self):
        self.timer.start()
        self.assertFalse(self.ended)
        time.sleep(0.8)
        self.timer.reset()
        self.assertFalse(self.ended)
        time.sleep(0.5)
        self.assertFalse(self.ended)
        time.sleep(0.6)
        self.assertTrue(self.ended)

    def test_timeout(self):
        self.timer.start()
        time.sleep(0.8)
        self.timer.reset()
        time.sleep(0.8)
        self.timer.reset()
        time.sleep(3.5)
        self.assertTrue(self.ended)

    def test_not_reset_after_timeout_reached(self):
        self.timer.start()
        time.sleep(0.8)
        self.timer.reset()
        time.sleep(0.8)
        self.timer.reset()
        time.sleep(0.8)
        self.timer.reset()
        time.sleep(0.8)
        self.assertTrue(self.ended)

    def has_triggered(self):
        self.ended = True
