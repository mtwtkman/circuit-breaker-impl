from unittest import TestCase
import time

from circuit_breaker import (
    OPEN, CLOSED, HALF_OPEN,
    CircuitBreakerOpenError, TimeoutError,
)


def noop():
    pass

def success():
    return True

def fail():
    raise Exception

def sleep(t):
    time.sleep(t)
    return 'done'


class CircuitBreakerTest(TestCase):
    def makeOne(self, circuit, invocation_timeout=None, failure_threshold=None, monitor=None):
        from circuit_breaker import CircuitBreaker
        return CircuitBreaker(
            circuit=circuit,
            invocation_timeout=invocation_timeout,
            failure_threshold=failure_threshold,
            monitor=monitor
        )
    def test_initial_state_is_closed(self):
        obj = self.makeOne(noop)
        self.assertEqual(obj.state, CLOSED)

    def test_stay_closed(self):
        obj = self.makeOne(success)
        obj.call()
        self.assertEqual(obj.state, CLOSED)

    def test_circuit_breaker_open_error_occurred(self):
        obj = self.makeOne(fail, failure_threshold=1)
        with self.assertRaises(Exception):
            obj.call()
        self.assertEqual(obj.state, OPEN)
        with self.assertRaises(CircuitBreakerOpenError):
            obj.call()

    def test_timeout(self):
        timeout = 0.1
        obj = self.makeOne(sleep, invocation_timeout=timeout, failure_threshold=1)
        with self.assertRaises(TimeoutError):
            obj.call(timeout + 0.1)
        self.assertEqual(obj.state, OPEN)
