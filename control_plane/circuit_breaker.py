import time

FAIL_THRESHOLD = 5
COOLDOWN_SECONDS = 120

class CircuitBreaker:

    def __init__(self):
        self.state = {}

    def _ensure(self, model):
        if model not in self.state:
            self.state[model] = {
                "failures": 0,
                "open_until": 0
            }

    def record_success(self, model):
        self._ensure(model)
        self.state[model]["failures"] = 0

    def record_failure(self, model):
        self._ensure(model)
        self.state[model]["failures"] += 1
        if self.state[model]["failures"] >= FAIL_THRESHOLD:
            self.state[model]["open_until"] = time.time() + COOLDOWN_SECONDS

    def is_open(self, model):
        self._ensure(model)
        if time.time() < self.state[model]["open_until"]:
            return True
        return False

breaker = CircuitBreaker()
