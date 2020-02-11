import sys
import threading
import time
from .errors import MaxAttempsError

if sys.version_info.major is 2:
    from aenum import Enum
else:
    from enum import Enum


class ConnectionStateChecker(object):
    def __init__(self,
                 ping_function,
                 keep_alive_interval,
                 sleep=10):
        self.sleep = sleep
        self.keep_alive_interval = keep_alive_interval
        self.last_message = time.time()
        self.ping_function = ping_function
        self.running = False
        self._thread = None
        if self.keep_alive_interval is None:
            self.keep_alive_interval = 10

    def start(self):
        self.running = True
        self._thread = threading.Thread(target=self.run)
        self._thread.daemon = True
        self._thread.start()

    def run(self):
        while self.running:
            time.sleep(self.sleep)
            time_without_messages = time.time() - self.last_message
            if self.keep_alive_interval < time_without_messages:
                self.ping_function()

    def stop(self):
        self.running = False


class ReconnectionType(Enum):
    raw = 0  # Reconnection with max reconnections and constant sleep time
    interval = 1  # variable sleep time


class ReconnectionHandler(object):
    def __init__(self,
                 start_function,
                 stop_function,
                 attempt_number=0):
        self.last_attempt = time.time()
        self.start_function = start_function
        self.stop_function = stop_function
        self.running = False
        self._thread = None
        self.reconnecting = False
        self.attempt_number = attempt_number
        self.exception = False

    def start(self):
        self.exception = False
        self.last_attempt = time.time()
        self.running = True
        self._thread = threading.Thread(target=self.run)
        self._thread.daemon = True
        self._thread.start()

    def run(self):
        while self.running:
            try:
                self.exception = False
                time_without_connection = time.time() - self.last_attempt
                print("RENUEW CONECTION time_without_connection", time_without_connection)
                self.stop_function()
                self.start_function()
                time.sleep(self.next())

            except MaxAttempsError:
                self.exception = True
                self.stop_function()

    def stop(self):
        self.running = False

    def next(self):
        raise NotImplementedError()

    def reset(self):
        self.attempt_number = 0


class RawReconnectionHandler(ReconnectionHandler):
    def __init__(self, start_function, stop_function, sleep_time, max_attempts):
        super(RawReconnectionHandler, self).__init__(start_function,
                                                     stop_function)

        self.sleep_time = sleep_time
        self.max_reconnection_attempts = max_attempts
        if max_attempts == 0:
            self.max_reconnection_attempts = None

    def next(self):
        # self.reconnecting = True
        if self.max_reconnection_attempts is not None:
            self.attempt_number += 1
            if self.attempt_number <= self.max_reconnection_attempts:
                return self.sleep_time
            else:
                raise MaxAttempsError(self.max_reconnection_attempts)
        else:  # Infinite reconnect
            return self.sleep_time


class IntervalReconnectionHandler(ReconnectionHandler):
    def __init__(self, start_function, stop_function, intervals):
        super(IntervalReconnectionHandler, self).__init__(start_function,
                                                          stop_function)
        self._intervals = intervals

    def next(self):
        # self.reconnecting = True
        try:
            index = self.attempt_number
            self.attempt_number += 1
            return self._intervals[index]
        except Exception:
            raise MaxAttempsError(0)
