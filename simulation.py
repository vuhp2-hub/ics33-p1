#!/usr/bin/env python3

import logger
from pathlib import Path

class Device:
    '''Device class with id and list of alerts'''
    _id_count = 0
    def __init__(self, logger: logger.Logger | None=None):
        '''Construct Device object. Id increment from class attribute'''
        self._alerts = []
        Device._id_count += 1
        self._id = Device._id_count
        self._prop_rules = []
        self._cancellation_times = {}
        self._logger = logger
    def add_prop_rule(self, receiver: Device, delay: int):
        '''Add popragation given device and delay'''
        assert receiver and type(delay) == int, "add_prop_rule: missing arguments device and delay"
        self._prop_rules.append((receiver, delay))
    def get_id(self):
        '''Returns device's id'''
        return self._id
    def alert(self, description: str, time_began: int, no_propagate=False) -> Alert:
        '''Creates a new alert given name and time begun'''
        assert description and type(time_began) == int, "Missing arguments"
        # Make Alerts (Or Blank alert due to cancellation) conflict and do nothing
        existing_alert = None
        for alert in self._alerts:
            if alert.get_description() == description:
                alert.change_time(time_began)
                existing_alert = alert
        if not existing_alert:
            existing_alert = Alert(description, time_began)
            self._alerts.append(existing_alert)
            if not no_propagate:
                self.propagate(existing_alert, time_began)

        return existing_alert
    def cancel_alert(self, description: str, time_cancelled: int):
        '''
        Cancels alert of the description.
        time_cancelled is the time the device is supposed to receive the cancellation
        '''
        assert description and type(time_cancelled) == int, "Missing arguments"
        for i in range(len(self._alerts)):
            alert = self._alerts[i]
            if alert.get_description() != description: continue
            if alert.is_propagation_ceased():
                return
            alert.cancel(time_cancelled)
            self.propagate(alert, time_cancelled)
    def propagate(self, alert: Alert, time_began: int):
        '''Propagates'''

        if alert.is_propagation_ceased(): return

        alert_desc = alert.get_description()
        if alert.is_cancelled():
            alert.set_propagation_ceased()

        for prop_rule in self._prop_rules:
            receiver = prop_rule[0]
            delay = prop_rule[1]
            time_received = time_began + delay

            if alert.is_cancelled():
                if self._logger:
                    self._logger.log_sent(time_began, "CANCELLATION", self.get_id(), receiver.get_id(), alert_desc)
                    self._logger.log_received(time_received, "CANCELLATION", receiver.get_id(), self.get_id(), alert_desc)
                receiver.cancel_alert(alert_desc, time_received)
            else:
                if self._logger:
                    self._logger.log_sent(time_began, "ALERT", self.get_id(), receiver.get_id(), alert_desc)
                    self._logger.log_received(time_received, "ALERT", receiver.get_id(), self.get_id(), alert_desc)                   
                receiver.alert(alert_desc, time_received)
class Alert:
    '''
    Alert class.
    An Alert class does not have an id because its alert's content
    is compared for the same description. For now, alert of the same description
    are allowed to coexist

    The attribute time is unique. Each Device should have their own
    alert. The _time attribute either means the time an alert
    was sent, or the time the alert was received.
    '''
    def __init__(self, description: str, time: int):
        '''Construct Alert object'''
        self._description = description
        self._time = time
        self._cancelled = False
        self._propagation_ceased = False
    def get_description(self) -> str:
        '''Returns the alert's description'''
        return self._description
    def get_time(self) -> int:
        '''Returns the alert's time'''
        return self._time
    def cancel(self, time_cancelled: int) -> bool:
        '''
        Cancels the alert
        '''
        if self._cancelled: return False
        self._cancelled = True
        self._time = time_cancelled
        return True
    def is_cancelled(self) -> bool:
        '''Returns a boolean telling of the alert is cancelled or not'''
        return self._cancelled
    def change_time(self, time: int):
        self._time = time
    def set_propagation_ceased(self):
        self._propagation_ceased = True
    def is_propagation_ceased(self):
        return self._propagation_ceased

class Simulation:
    def __init__(self):
        self._logger = None
        self._devices = {}
        self._initial_alerts_queue = []
        self._initial_cancellations_queue = []
    def set_length(self, length):
        '''Initializes logger'''
        self._logger = logger.Logger(length)
    def add_device(self, device_id: str):
        '''Add devices to simulation list'''
        assert self._logger
        self._devices[device_id] = Device(self._logger)
    def add_propagation(self, propagator_id: str, propagatee_id: str, delay: str):
        '''Add propagation rule'''
        self._devices[propagator_id].add_prop_rule(self._devices[propagatee_id], int(delay))
    def add_alert(self, device_id: str, message: str, time_begin: str):
        '''Add Alert to queue to be run'''
        self._initial_alerts_queue.append((device_id, message, time_begin))
    def add_cancellation_time(self, device_id: str, message: str, time_begin: str):
        '''Add cancellation times'''
        self._initial_cancellations_queue.append((device_id, message, time_begin))
    def run(self):
        '''Runs the simulation'''
        assert self._devices and self._logger and self._initial_alerts_queue
        for alert in self._initial_alerts_queue:
            self._devices[alert[0]].alert(alert[1], int(alert[2]))
        for alert in self._initial_cancellations_queue:
            self._devices[alert[0]].cancel_alert(alert[1], int(alert[2]))
        print(self._logger.organize_log())
