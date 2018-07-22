from unittest import TestCase
import time

from circuit_breaker import (
    OPEN, CLOSED, HALF_OPEN,
    CircuitBreakerOpenError, TimeoutError,
)


class SomethingWrong(Exception):
    pass


def noop():
    pass


def success():
    return True


def fail():
    raise SomethingWrong


def sleep(t):
    time.sleep(t)
    return 'done'


class CircuitBreakerTest(TestCase):
    def setUp(self):
        self.invocation_timeout = 0.01
        self.reset_timeout = 0.1
        self.failure_threshold = 1

    def makeOne(
        self,
        circuit,
        invocation_timeout=None,
        failure_threshold=None,
        reset_timeout=None,
    ):
        from circuit_breaker import CircuitBreaker
        return CircuitBreaker(
            circuit=circuit,
            invocation_timeout=invocation_timeout or self.invocation_timeout,
            failure_threshold=failure_threshold or self.failure_threshold,
            reset_timeout=reset_timeout or self.reset_timeout,
        )
    def test_initial_state_is_closed(self):
        obj = self.makeOne(noop)
        self.assertEqual(obj.state, CLOSED)

    def test_stay_closed(self):
        obj = self.makeOne(success)
        obj.call()
        self.assertEqual(obj.state, CLOSED)

    def test_circuit_breaker_open_error_occurred(self):
        obj = self.makeOne(fail)
        with self.assertRaises(SomethingWrong):
            obj.call()
        self.assertEqual(obj.state, OPEN)
        with self.assertRaises(CircuitBreakerOpenError):
            obj.call()

    def test_timeout_and_over_threashold(self):
        obj = self.makeOne(sleep)
        with self.assertRaises(TimeoutError):
            obj.call(self.invocation_timeout + 0.1)
        self.assertEqual(obj.state, OPEN)

    def test_timeout_and_within_threashold(self):
        obj = self.makeOne(sleep, failure_threshold=2)
        try:
            obj.call(self.invocation_timeout + 0.1)
        except:
            pass
        self.assertEqual(obj.state, CLOSED)

    def test_never_call_function_when_not_reached_reset_timeout(self):
        obj = self.makeOne(fail, reset_timeout=10)
        try:
            obj.call()
        except:
            pass
        with self.assertRaises(CircuitBreakerOpenError):
            obj.call()

    def test_half_open(self):
        obj = self.makeOne(fail, reset_timeout=-1.0)
        try:
            obj.call()
        except:
            pass
        self.assertEqual(obj.state, HALF_OPEN)

    def test_half_open_can_call_function(self):
        obj = self.makeOne(fail, reset_timeout=-1.0)
        try:
            obj.call()
        except:
            pass
        with self.assertRaises(SomethingWrong):
            obj.call()
            self.assertEqual(obj.state, OPEN)

    def test_half_open_transit_to_closed_when_succeded(self):
        obj = self.makeOne(sleep)
        try:
            obj.call(self.invocation_timeout + 0.1)
        except:
            pass
        time.sleep(self.reset_timeout)
        self.assertEqual(obj.state, HALF_OPEN)
        obj.call(self.invocation_timeout - 0.001)
        self.assertEqual(obj.state, CLOSED)

    def test_half_open_transit_to_open_when_failed(self):
        obj = self.makeOne(sleep)
        try:
            obj.call(self.invocation_timeout + 0.1)
        except:
            pass
        time.sleep(self.reset_timeout)
        self.assertEqual(obj.state, HALF_OPEN)
        with self.assertRaises(TimeoutError):
            obj.call(self.invocation_timeout)
        self.assertEqual(obj.state, OPEN)
