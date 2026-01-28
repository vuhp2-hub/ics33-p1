#!/usr/bin/env python3

class Device:
    '''Device class with id and list of alerts'''
    _id_count = 0
    def __init__(self):
        '''Construct Device object. Id increment from class attribute'''
        self._alerts = []
        Device._id_count += 1
        self._id = Device._id_count
    def get_id(self):
        '''Returns device's id'''
        return self._id
    def alert(self, description: str, time_began: int) -> Alert:
        '''Creates a new alert given name and time begun'''
        assert description and type(time_began) == int, "Missing arguments"
        # Make Alerts (Or Blank alert due to cancellation) conflict and do nothing
        for existing_alert in self._alerts:
            if existing_alert.get_description() == description:
                existing_alert.change_time(time_began)
                return existing_alert
        alert = Alert(description, time_began)
        self._alerts.append(alert)
        return alert
    def cancel_alert(self, description: str, time_cancelled: int):
        '''Cancels alert of the description
        time_cancelled is the time the device is supposed to receive the cancellation
        '''
        assert description and type(time_cancelled) == int, "Missing arguments"
        alert_exists = False
        for alert in self._alerts:
            if alert.get_description() != description: continue
            alert_exists = True
            if alert.get_time() >= time_cancelled: return
            alert.cancel(time_cancelled)
        if alert_exists: return
        # Cancellation arrives early? --> Sets up blank alert
        alert = self.alert(description, time_cancelled)
        alert.cancel(time_cancelled)
    def propagate(self, receiver: Device, time_delay: int):
        '''Propagates alerts'''
        assert receiver, "No Device receiver as argument"
        for alert in self._alerts:
            alert_message = alert.get_description()
            time_received = alert.get_time() + time_delay
            if alert.is_cancelled():
                receiver.cancel_alert(alert_message, time_received)
            else:
                receiver.alert(alert_message, time_received)
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
