#!/usr/bin/env python3

import unittest
from simulation import Device, Alert

class TestAlert(unittest.TestCase):
    def setUp(self):
        self._alert = Alert("We all say 'Boo'", 1000)

    def test_alert_init(self):
        self.assertEqual(self._alert.get_message(), "We all say 'Boo'")
        self.assertEqual(self._alert.get_time(), 1000)

    def test_cancel_alert(self):
        self._alert.cancel()
        self.assertEqual(self._alert.is_cancelled(), True)

class TestDevice(unittest.TestCase):
    def setUp(self):
        self._devices = [Device(), Device(), Device()]
    def test_devices_init(self):
        self.assertEqual(Device._id_count, 3)
        for i in range(len(self._devices)):
            self.assertEqual(self._devices[i].get_id(), i+1)
