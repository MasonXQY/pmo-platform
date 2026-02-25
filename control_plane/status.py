from .circuit_breaker import breaker
from .database import get_metrics


def model_status():
    return {
        "circuit_state": breaker.state,
        "metrics": get_metrics()
    }
