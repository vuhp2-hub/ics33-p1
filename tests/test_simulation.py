#!/usr/bin/env python3
import unittest

from simulation import Device, Alert, Simulation

def lines(output: str) -> set[str]:
    """Split into non-empty lines for order-insensitive comparisons."""
    return set([ln for ln in output.splitlines() if ln.strip() != ""])

class TestAlert(unittest.TestCase):
    def setUp(self):
        self._alert = Alert("We all say 'Boo'", 1000)

    def test_alert_init(self):
        self.assertEqual(self._alert.get_description(), "We all say 'Boo'")
        self.assertEqual(self._alert.get_time(), 1000)
        self.assertFalse(self._alert.is_cancelled())

    def test_cancel_alert(self):
        self.assertTrue(self._alert.cancel(2000))
        self.assertTrue(self._alert.is_cancelled())
        self.assertEqual(self._alert.get_time(), 2000)

    def test_cancel_twice_returns_false(self):
        self.assertTrue(self._alert.cancel(2000))
        self.assertFalse(self._alert.cancel(3000))
        self.assertEqual(self._alert.get_time(), 2000)

class TestDevice(unittest.TestCase):
    def setUp(self):
        Device._id_count = 0
        self._devices = [Device(), Device(), Device()]

    def test_devices_init(self):
        self.assertEqual(Device._id_count, 3)
        for i, d in enumerate(self._devices):
            self.assertEqual(d.get_id(), i + 1)

    def test_add_prop_rule(self):
        d1, d2 = self._devices[0], self._devices[1]
        d1.add_prop_rule(d2, 750)
        self.assertEqual(len(d1._prop_rules), 1)
        neighbor, delay = d1._prop_rules[0]
        self.assertIs(neighbor, d2)
        self.assertEqual(delay, 750)

    def test_seen_cancels_starts_empty(self):
        self.assertEqual(self._devices[0]._seen_cancels, set())

class TestSimulationSetup(unittest.TestCase):
    def setUp(self):
        Device._id_count = 0
        self.sim = Simulation()
        self.sim.set_length(100000)

    def test_simulation_logger_init(self):
        self.assertIsNotNone(self.sim._logger)
        self.assertEqual(self.sim._length, 100000)

    def test_add_device(self):
        self.sim.add_device("1")
        self.assertIn("1", self.sim._devices)

    def test_add_propagation(self):
        self.sim.add_device("1")
        self.sim.add_device("2")
        self.sim.add_propagation("1", "2", "100")

        d1 = self.sim._devices["1"]
        self.assertEqual(len(d1._prop_rules), 1)
        neighbor, delay = d1._prop_rules[0]
        self.assertEqual(neighbor.get_id(), self.sim._devices["2"].get_id())
        self.assertEqual(delay, 100)

    def test_add_alert_enqueue(self):
        self.sim.add_alert("1", "Hello", "500")
        self.assertEqual(self.sim._initial_alerts_queue, [("1", "Hello", "500")])

    def test_add_cancellation_time_enqueue(self):
        self.sim.add_cancellation_time("1", "Hello", "600")
        self.assertEqual(self.sim._cancellations_queue["1"]["Hello"], 600)

class TestPropagation(unittest.TestCase):
    def setUp(self):
        Device._id_count = 0

    def test_propagate_runs_and_logs_something_nontrivial(self):
        sim = Simulation()
        sim.set_length(50)

        for did in ["1", "2", "3", "4", "5"]:
            sim.add_device(did)

        # A directed cycle with short delays
        sim.add_propagation("1", "2", "1")
        sim.add_propagation("2", "3", "1")
        sim.add_propagation("3", "4", "1")
        sim.add_propagation("4", "5", "1")
        sim.add_propagation("5", "1", "1")

        # Extra chords (creates simultaneous events sometimes)
        sim.add_propagation("1", "3", "2")
        sim.add_propagation("2", "4", "2")
        sim.add_propagation("3", "5", "2")

        # Seed multiple alerts at different times
        sim.add_alert("1", "A1", "0")
        sim.add_alert("3", "A2", "5")

        # Seed cancellations (after alerts have had time to spread)
        sim.add_cancellation_time("1", "A1", "15")
        sim.add_cancellation_time("3", "A2", "20")

        # Run propagation
        sim._propagate()
        out = sim._logger.organize_log()
        out_lines = out.splitlines()

        # END line must exist and be correct
        self.assertTrue(out_lines, "No output produced at all")
        self.assertEqual(out_lines[-1], "@50: END")

        # Ensure we logged at least one of each major kind
        joined = "\n".join(out_lines)
        self.assertIn("SENT ALERT", joined, "Expected at least one SENT ALERT log")
        self.assertIn("RECEIVED ALERT", joined, "Expected at least one RECEIVED ALERT log")
        self.assertIn("SENT CANCELLATION", joined, "Expected at least one SENT CANCELLATION log")
        self.assertIn("RECEIVED CANCELLATION", joined, "Expected at least one RECEIVED CANCELLATION log")

        # Sanity-check that every log line time is within [0, LENGTH]
        # (excluding END which is exactly LENGTH)
        for line in out_lines:
            if not line.startswith("@"):
                self.fail(f"Malformed log line: {line}")

            # line format: "@<time>: ..."
            time_part = line.split(":", 1)[0][1:]  # strip leading '@'
            self.assertTrue(time_part.isdigit(), f"Non-numeric time in line: {line}")
            t = int(time_part)
            self.assertGreaterEqual(t, 0, f"Negative time in line: {line}")
            self.assertLessEqual(t, 50, f"Time beyond length in line: {line}")
