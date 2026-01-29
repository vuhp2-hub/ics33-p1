#!/usr/bin/env python3

import unittest
from simulation import Device, Alert, Simulation

class TestAlert(unittest.TestCase):
    def setUp(self):
        self._alert = Alert("We all say 'Boo'", 1000)

    def test_alert_init(self):
        self.assertEqual(self._alert.get_description(), "We all say 'Boo'")
        self.assertEqual(self._alert.get_time(), 1000)
        self.assertFalse(self._alert.is_cancelled())

    def test_cancel_alert(self):
        self.assertTrue(self._alert.cancel(2000))   # first cancel returns True
        self.assertTrue(self._alert.is_cancelled())
        self.assertEqual(self._alert.get_time(), 2000)

    def test_cancel_alert_twice_returns_false(self):
        self.assertTrue(self._alert.cancel(2000))
        self.assertFalse(self._alert.cancel(3000))  # second cancel returns False
        self.assertEqual(self._alert.get_time(), 2000)  # time unchanged


class TestDevice(unittest.TestCase):
    def setUp(self):
        Device._id_count = 0
        self._devices = [Device(), Device(), Device()]

    def test_devices_init(self):
        self.assertEqual(Device._id_count, 3)
        for i in range(len(self._devices)):
            self.assertEqual(self._devices[i].get_id(), i + 1)

    def test_add_prop_rule(self):
        d1, d2 = self._devices[0], self._devices[1]
        d1.add_prop_rule(d2, 750)
        self.assertEqual(len(d1._prop_rules), 1)
        neighbor, delay = d1._prop_rules[0]
        self.assertIs(neighbor, d2)
        self.assertEqual(delay, 750)

    def test_seen_cancels_starts_empty(self):
        d = self._devices[0]
        self.assertEqual(d._seen_cancels, set())


class TestSimulation(unittest.TestCase):
    def setUp(self):
        self._simulation = Simulation()
        self._simulation.set_length(100000)

    def test_simulation_logger_init(self):
        self.assertIsNotNone(self._simulation._logger)
        self.assertEqual(self._simulation._length, 100000)

    def test_add_device(self):
        self._simulation.add_device("1")
        self.assertIn("1", self._simulation._devices)

    def test_add_propagation(self):
        self._simulation.add_device("1")
        self._simulation.add_device("2")
        self._simulation.add_propagation("1", "2", "100")

        d1 = self._simulation._devices["1"]
        self.assertEqual(len(d1._prop_rules), 1)
        _, delay = d1._prop_rules[0]
        self.assertEqual(delay, 100)

    def test_add_alert_enqueue(self):
        self._simulation.add_alert("1", "Hello", "500")
        self.assertEqual(self._simulation._initial_alerts_queue, [("1", "Hello", "500")])

    def test_add_cancellation_time_enqueue(self):
        self._simulation.add_cancellation_time("1", "Hello", "600")
        self.assertIn("1", self._simulation._cancellations_queue)
        self.assertEqual(self._simulation._cancellations_queue["1"]["Hello"], 600)
