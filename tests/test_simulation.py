#!/usr/bin/env python3

import unittest
from simulation import Device, Alert

class TestAlert(unittest.TestCase):
    def setUp(self):
        self._alert = Alert("We all say 'Boo'", 1000)

    def test_alert_init(self):
        self.assertEqual(self._alert.get_description(), "We all say 'Boo'")
        self.assertEqual(self._alert.get_time(), 1000)

    def test_cancel_alert(self):
        self._alert.cancel(2000)
        self.assertEqual(self._alert.is_cancelled(), True)
        self.assertEqual(self._alert.get_time(), 2000)

class TestDevice(unittest.TestCase):
    def setUp(self):
        Device._id_count = 0
        self._devices = [Device(), Device(), Device()]
    def test_devices_init(self):
        self.assertEqual(Device._id_count, 3)
        for i in range(len(self._devices)):
            self.assertEqual(self._devices[i].get_id(), i+1)
    def test_device_alert(self):
        device = self._devices[0]
        device.alert("Hello", 1000)
        self.assertTrue(device._alerts)
        self.assertEqual(device._alerts[0].get_time(), 1000)
    def test_alert_same_description_no_duplicate_time_updated(self):
        device = self._devices[0]
        device.alert("Hello", 1000)
        device.alert("Hello", 2000)
        self.assertEqual(len(device._alerts), 1)
        self.assertEqual(device._alerts[0].get_time(), 2000)
    def test_cancel_alert(self):
        device = self._devices[0]
        device.alert("Hello", 1000)
        self.assertEqual(device._alerts[0].get_time(), 1000)
        device.cancel_alert("Hello", 2000)
        self.assertTrue(device._alerts[0].is_cancelled())
        self.assertEqual(device._alerts[0].get_time(), 2000)
    def test_cancel_alert_no_existing_alert(self):
        device = self._devices[0]
        device.cancel_alert("Hello", 2000)
        self.assertTrue(device._alerts[0].is_cancelled())
        self.assertEqual(device._alerts[0].get_time(), 2000)
    def test_device_propagation(self):
        device1 = self._devices[0]
        device2 = self._devices[1]
        device3 = self._devices[2]

        device1.alert("Hello", 0)
        device1.propagate(device2, 1000)
        self.assertTrue(device2._alerts)
        self.assertEqual(device2._alerts[0].get_time(), 1000)
        device2.propagate(device3, 2000)
        self.assertEqual(device3._alerts[0].get_time(), 3000)
        self.assertEqual(device3._alerts[0].get_description(), "Hello")
