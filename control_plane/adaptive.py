from .database import get_metrics
from .performance import model_win_rates

class AdaptiveOptimizer:

    def get_model_stats(self):
        return get_metrics()

    def get_win_rates(self):
        return model_win_rates()

    def select_optimal(self, prompt_type="balanced"):
        metrics = self.get_model_stats()
        wins = self.get_win_rates()

        # Fallback default
        if not metrics:
            return "kimi"

        # Deep reasoning always prefer opus
        if prompt_type == "deep_reasoning":
            return "opus"

        # Fast tasks → lowest latency
        if prompt_type == "fast":
            return min(metrics, key=lambda m: metrics[m].get("avg_latency_ms", 9999))

        # Balanced → weighted decision: win_rate prioritized, then cost
        best_model = None
        best_score = -1

        for model, data in metrics.items():
            win_rate = wins.get(model, {}).get("win_rate", 0)
            cost = data.get("total_cost", 0)

            # Score formula: prioritize win rate, penalize high cost
            score = (win_rate * 2) - (cost * 0.1)

            if score > best_score:
                best_score = score
                best_model = model

        return best_model or "kimi"
