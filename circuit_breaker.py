from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, TimeoutError


OPEN = 'open'
CLOSED = 'closed'
HALF_OPEN = 'half_open'


class CircuitBreakerOpenError(Exception):
    pass


class CircuitBreaker:
    def __init__(
        self,
        circuit,
        invocation_timeout=None,
        failure_threshold=None,
        reset_timeout=None,
        monitor=None,
        max_workers=None,
    ):
        self.circuit = circuit
        self.invocation_timeout = invocation_timeout or 10.0
        self.failure_threshold = failure_threshold or 5
        self.reset_timeout = timedelta(seconds=reset_timeout or 0.1)
        self.monitor = monitor or CircuitBreakerMonitor()
        self.max_workers = max_workers or 1
        self.reset()

    def reset(self):
        self.failure_count = 0
        self.last_failure_time = None
        self.monitor.alert('reset_circuit')

    @property
    def is_over_threshold(self):
        return self.failure_count >= self.failure_threshold

    @property
    def is_over_failure_time(self):
        return datetime.now() - self.last_failure_time > self.reset_timeout

    @property
    def state(self):
        if  self.is_over_threshold and self.is_over_failure_time:
            return HALF_OPEN
        elif self.is_over_threshold:
            return OPEN
        else:
            return CLOSED

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        if self.state == OPEN:
            self.monitor.alert('open circuit')

    def call(self, *args, **kwargs):
        if self.state in (CLOSED, HALF_OPEN):
            try:
                return self.do_call(*args, **kwargs)
            except (TimeoutError, Exception) as e:
                self.record_failure()
                raise
        elif self.state == OPEN:
            raise CircuitBreakerOpenError

    def do_call(self, *args, **kwargs):
        with ThreadPoolExecutor(max_workers=self.max_workers) as e:
            return e.submit(self.circuit, *args, **kwargs) \
                    .result(timeout=self.invocation_timeout)


class CircuitBreakerMonitor:
    def alert(self, msg):
        print(msg)
