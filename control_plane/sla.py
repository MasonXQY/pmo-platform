from .database import get_metrics, get_daily_cost
from .circuit_breaker import breaker

DAILY_COST_LIMIT = 1.0  # configurable enterprise threshold
ERROR_RATE_THRESHOLD = 0.2  # 20%

class SLAController:

    def evaluate(self):
        metrics = get_metrics()
        daily_cost = get_daily_cost()

        actions = []

        # Daily cost protection
        if daily_cost > DAILY_COST_LIMIT:
            actions.append("DAILY_COST_LIMIT_EXCEEDED")

        # Error-rate based degradation
        for model, data in metrics.items():
            calls = data.get("calls", 0)
            errors = data.get("total_errors", 0)

            if calls > 0:
                error_rate = errors / calls
                if error_rate > ERROR_RATE_THRESHOLD:
                    breaker.record_failure(model)
                    actions.append(f"HIGH_ERROR_RATE_{model}")

        return {
            "daily_cost": daily_cost,
            "metrics": metrics,
            "actions": actions
        }

sla_controller = SLAController()
