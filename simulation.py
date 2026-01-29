#!/usr/bin/env python3

import logger

class Device:
    '''Device class with id and list of alerts'''
    _id_count = 0
    def __init__(self):
        '''Construct Device object. Id increment from class attribute'''
        Device._id_count += 1
        self._id = Device._id_count
        self._prop_rules = []
        self._seen_cancels = set()
    def add_prop_rule(self, receiver: Device, delay: int):
        '''Add popragation given device and delay'''
        assert receiver and type(delay) == int, "add_prop_rule: missing arguments device and delay"
        self._prop_rules.append((receiver, delay))
    def get_id(self):
        '''Returns device's id'''
        return self._id
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
        self._cancellations_queue = {}
        self._length = None
    def set_length(self, length):
        '''Initializes logger'''
        self._length = length
        self._logger = logger.Logger(length)
    def add_device(self, device_id: str):
        '''Add devices to simulation list'''
        assert self._logger
        self._devices[device_id] = Device()
    def add_propagation(self, propagator_id: str, propagatee_id: str, delay: str):
        '''Add propagation rule'''
        self._devices[propagator_id].add_prop_rule(self._devices[propagatee_id], int(delay))
    def add_alert(self, device_id: str, message: str, time_begin: str):
        '''Add Alert to queue to be run'''
        self._initial_alerts_queue.append((device_id, message, time_begin))
    def add_cancellation_time(self, device_id: str, message: str, time_begin: str):
        '''Add cancellation times'''
        if not device_id in self._cancellations_queue:
            self._cancellations_queue[device_id] = {}
        self._cancellations_queue[device_id][message] = int(time_begin)
    def _propagate(self):
        '''Propagation logic'''
        assert self._logger

        length = self._length

        # Build initial event queue:
        # event = (time, kind, src_device_obj, dst_device_obj, description, seeded)
        # seeded=True means "raised by device itself" (no RECEIVED line, only SENTs)
        events = []

        # Seed ALERT raises
        for (dev_id, desc, t) in self._initial_alerts_queue:
            t = int(t)
            dev = self._devices[dev_id]
            events.append((t, "ALERT", dev, dev, desc, True))

        # Seed CANCELLATION raises
        for dev_id, mapping in self._cancellations_queue.items():
            dev = self._devices[dev_id]
            for desc, t in mapping.items():
                events.append((int(t), "CANCELLATION", dev, dev, desc, True))

        # Process events in time order; batch by same time to support the "n+1" rule
        while events:
            # pick next time
            events.sort(key=lambda e: e[0])
            current_time = events[0][0]

            # Stop at end time: nothing happens at time == LENGTH
            if length is not None and current_time >= int(length):
                break

            # Take batch with same timestamp
            batch = []
            while events and events[0][0] == current_time:
                batch.append(events.pop(0))

            # Snapshot cancels before this time (n+1 rule)
            canceled_before = {d.get_id(): set(d._seen_cancels) for d in self._devices.values()}
            cancels_to_apply = []  # (dst_device_obj, desc)

            for (t, kind, src, dst, desc, seeded) in batch:
                # Log RECEIVED for real network deliveries (not for initial raises)
                if not seeded and src.get_id() != dst.get_id():
                    self._logger.log_received(t, kind, dst.get_id(), src.get_id(), desc)

                if kind == "ALERT":
                    # If canceled before this time, do not forward
                    if desc in canceled_before[dst.get_id()]:
                        continue

                    # If canceled before this time, do not forward
                    if desc in canceled_before[dst.get_id()]:
                        continue

                    # Immediately send to propagation set (EVERY time we receive it)
                    for (neighbor, delay) in dst._prop_rules:
                        recv_time = t + delay
                        if length is not None and recv_time >= int(length):
                            continue

                        self._logger.log_sent(t, "ALERT", dst.get_id(), neighbor.get_id(), desc)
                        events.append((recv_time, "ALERT", dst, neighbor, desc, False))
                else:  # CANCELLATION
                    # Forward cancellation at most once per device
                    if desc in dst._seen_cancels:
                        # already known cancel; no forward
                        continue

                    # n+1 rule: cancellation becomes effective AFTER all events at time t are processed
                    cancels_to_apply.append((dst, desc))

                    # Immediately send cancellation to propagation set
                    for (neighbor, delay) in dst._prop_rules:
                        recv_time = t + delay
                        if length is not None and recv_time >= int(length):
                            continue

                        self._logger.log_sent(t, "CANCELLATION", dst.get_id(), neighbor.get_id(), desc)
                        events.append((recv_time, "CANCELLATION", dst, neighbor, desc, False))

            # Apply cancellations after the batch (so they affect time t+1 onward)
            for (dst, desc) in cancels_to_apply:
                dst._seen_cancels.add(desc)

    def run(self):
        '''Runs the simulation'''
        assert self._devices and self._logger
        self._propagate()
        print(self._logger.organize_log())
