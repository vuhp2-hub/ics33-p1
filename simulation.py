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
            if not no_propagate:
                self._alerts.append(existing_alert)
        if not no_propagate:
            self.propagate(existing_alert, time_began)
        return existing_alert
    def _cancel_alert(self, description: str, time_cancelled: int):
        '''
        Cancels alert of the description.
        time_cancelled is the time the device is supposed to receive the cancellation
        '''
        assert description and type(time_cancelled) == int, "Missing arguments"
        for i in range(len(self._alerts)):
            alert = self._alerts[i]
            if alert.get_description() != description: continue
            assert alert.get_time() < time_cancelled
            if alert.is_cancelled(): return
            alert.cancel(time_cancelled)
            self.propagate(alert, time_cancelled)
            return
        # assume alert has not have time to be created
        alert = self.alert(description, time_cancelled, no_propagate=True)
        alert.cancel(time_cancelled)
        self._alerts.append(alert)
        self.propagate(alert, time_cancelled)
    def propagate(self, alert: Alert, time_began: int):
        '''Propagates'''

        alert_desc = alert.get_description()

        for prop_rule in self._prop_rules:
            receiver = prop_rule[0]
            delay = prop_rule[1]
            time_received = time_began + delay
            if alert_desc in self._cancellation_times:
                receiver._cancellation_times[alert_desc] = self._cancellation_times[alert_desc]
                if self._cancellation_times[alert_desc] < time_received:
                    if not alert.is_cancelled():
                        if self._logger:
                            self._logger.log_sent(time_began, 'CANCELLATION', self.get_id(), receiver.get_id(), alert_desc)
                            self._logger.log_received(time_received, 'CANCELLATION', receiver.get_id(), self.get_id(), alert_desc)
                        self._cancel_alert(alert_desc, time_received)
                    else:
                        if self._logger:
                            self._logger.log_sent(time_began, 'CANCELLATION', self.get_id(), receiver.get_id(), alert_desc)
                            self._logger.log_received(time_received, 'CANCELLATION', receiver.get_id(), self.get_id(), alert_desc)
                        receiver._cancel_alert(alert_desc, time_received)
                else:
                    # UGLY CODE: no time to fix :(
                    if self._logger:
                        self._logger.log_sent(time_began, 'ALERT', self.get_id(), receiver.get_id(), alert_desc)
                        self._logger.log_received(time_received, 'ALERT', receiver.get_id(), self.get_id(), alert_desc)
                    receiver.alert(alert_desc, time_received)
            else:
                if self._logger:
                    self._logger.log_sent(time_began, 'ALERT', self.get_id(), receiver.get_id(), alert_desc)
                    self._logger.log_received(time_received, 'ALERT', receiver.get_id(), self.get_id(), alert_desc)
                receiver.alert(alert_desc, time_received)
    def set_cancellation_time(self, description: str, time: int):
        self._cancellation_times[description] = time
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

class Simulation:
    def __init__(self):
        self._logger = None
        self._devices = {}
        self._initial_alerts_queue = []
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
        self._devices[device_id].set_cancellation_time(message, int(time_begin))
    def run(self):
        '''Runs the simulation'''
        assert self._devices and self._logger and self._initial_alerts_queue
        for alert in self._initial_alerts_queue:
            self._devices[alert[0]].alert(alert[1], int(alert[2]))
        print(self._logger.organize_log())
