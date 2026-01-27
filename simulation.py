#!/usr/bin/env python3

class Device:
    '''Device class with id and list of alerts'''
    _id_count = 0
    def __init__(self):
        '''Construct Device object. Id increment from class attribute'''
        self.alerts = []
        Device._id_count += 1
        self._id = Device._id_count
    def get_id(self):
        '''Returns device's id'''
        return self._id
    def send_alert(self, message: str, time_received: int, device: Device):
        '''Send a new alert'''
        pass
    def accept_alert(self, message: str, time_received: int, device: Device):
        '''Creates the object's own alert'''
        pass

class Alert:
    '''
    Alert class.
    An Alert class does not have an id because its alert's content
    is compared for the same message. If another alert with
    the same message is created, the manager of the collection
    of alerts should delete the alert with the same message.

    The attribute time is unique. Each Device should have their own
    alert. The _time attribute either means the time an alert
    was sent, or the time the alert was received.
    '''
    def __init__(self, message: str, time: int):
        '''Construct Alert object'''
        self._message = message
        self._time = time
        self._cancelled = False
    def get_message(self) -> str:
        '''Returns the alert's message'''
        return self._message
    def get_time(self) -> int:
        '''Returns the alert's time'''
        return self._time
    def cancel(self) -> bool:
        if self._cancelled: return False
        self._cancelled = True
        return True
    def is_cancelled(self) -> bool:
        return self._cancelled
    

