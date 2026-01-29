#!/usr/bin/env python3

class Logger:
    '''This class logs the simulation'''
    def __init__(self, length: int):
        self._time_log = {}
        self._sorted_time_keys = []
        self._length = length
    def log_received(self, time: int, alert_type: str, recipient: int, sender: int, description: str):
        '''Logs recieved'''
        assert alert_type and (alert_type == "CANCELLATION" or alert_type == "ALERT")
        assert description
        if not str(time) in self._time_log:
            self._sorted_time_keys.append(time)
            self._sorted_time_keys.sort()
            self._time_log[time] = []
        self._time_log[time].append(f'#{recipient} RECEIVED {alert_type} FROM #{sender}: {description}')

    def log_sent(self, time: int, alert_type: str, sender: int, recipient: int, description: str):
        '''Logs sent'''
        assert alert_type and (alert_type == "CANCELLATION" or alert_type == "ALERT")
        assert description
        if not str(time) in self._time_log:
            self._sorted_time_keys.append(time)
            self._sorted_time_keys.sort()
            self._time_log[time] = []
        self._time_log[time].append(f'#{sender} SENT {alert_type} TO #{recipient}: {description}')       

    def organize_log(self) -> str:
        '''Organize log and return it'''
        result = ''
        for time_key in self._sorted_time_keys:
            assert time_key in self._time_log
            for time_log in self._time_log[time_key]:
                result += f'@{time_key}: {time_log}\n'
        result += f'@{self._length}: END'
        return result
