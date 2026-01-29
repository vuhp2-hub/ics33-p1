#!/usr/bin/env python3

from logger import Logger

import unittest
class TestLogger(unittest.TestCase):
    def setUp(self):
        self._logger = Logger(100000)
    def test_log_received(self):
        self._logger.log_received(1000, "ALERT", 2, 1, "Hi")
        self.assertEqual(self._logger._time_log[1000][0], '#2 RECEIVED ALERT FROM #1: Hi')
    def test_log_sent(self):
        self._logger.log_sent(1000, "ALERT", 1, 2, "Hi")
        self.assertEqual(self._logger._time_log[1000][0], '#1 SENT ALERT TO #2: Hi')
    def test_logger_organized(self):
        self._logger.log_sent(1000, "ALERT", 1, 2, "Hi")
        self._logger.log_received(2000, "ALERT", 2, 1, "Hi")
        self.assertEqual(self._logger.organize_log(), "@1000: #1 SENT ALERT TO #2: Hi\n@2000: #2 RECEIVED ALERT FROM #1: Hi\n@100000: END")
