import asyncio
from asyncio import Semaphore
from .agents import KimiAgent, ClaudeAgent, AzureGPTAgent
from .observability import observability
from .cost_model import estimate_cost
from .database import record_request
from .judge import Judge
from .cache import get_cached, set_cache, init_cache
from .adaptive import AdaptiveOptimizer
from .logging import log_event, hash_prompt
from .circuit_breaker import breaker
from .model_registry import is_enabled
from .performance import record_ensemble_result

BUDGET_LIMIT = 0.05
CONCURRENCY_LIMIT = 10

semaphore = Semaphore(CONCURRENCY_LIMIT)

class Router:

    def __init__(self):
        self.kimi = KimiAgent()
        self.opus = ClaudeAgent("claude-opus-4-6")
        self.sonnet = ClaudeAgent("claude-sonnet-4-6")
        self.azure = AzureGPTAgent()
        self.judge = Judge()
        self.adaptive = AdaptiveOptimizer()
        init_cache()

    async def ensemble(self, prompt):
        async with semaphore:
            prompt_hash = hash_prompt(prompt)

            tasks = {
                "kimi": asyncio.create_task(self._call_model("kimi", prompt)),
                "opus": asyncio.create_task(self._call_model("opus", prompt)),
                "sonnet": asyncio.create_task(self._call_model("sonnet", prompt)),
                "azure": asyncio.create_task(self._call_model("azure", prompt))
            }

            results = {}
            for name, task in tasks.items():
                try:
                    data = await task
                    results[name] = data["output"]
                except Exception as e:
                    results[name] = f"ERROR: {e}"

            best_model, confidence = await self.judge.evaluate(prompt, results)

            record_ensemble_result("default", best_model, confidence)

            log_event({
                "event": "ensemble_decision",
                "selected_model": best_model,
                "confidence": confidence,
                "prompt_hash": prompt_hash
            })

            return {
                "selected_model": best_model,
                "confidence": confidence,
                "response": results.get(best_model),
                "all_responses": results
            }
