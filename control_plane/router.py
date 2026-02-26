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

    async def _call_model(self, model, prompt):
        if not is_enabled(model):
            raise Exception(f"Model {model} disabled by admin")

        if breaker.is_open(model):
            raise Exception(f"Circuit open for {model}")

        try:
            if model == "kimi":
                result_data = await self.kimi.run(prompt)
            elif model == "opus":
                result_data = await self.opus.run(prompt)
            elif model == "sonnet":
                result_data = await self.sonnet.run(prompt)
            elif model == "azure":
                result_data = await self.azure.run(prompt)
            else:
                raise ValueError("Unknown model")

            breaker.record_success(model)
            return result_data

        except Exception as e:
            breaker.record_failure(model)
            raise e

    async def single_route(self, model, prompt):
        async with semaphore:
            request_id, start = observability.start()

            result_data = await self._call_model(model, prompt)

            output = result_data["output"]
            tokens = result_data["tokens"]

            latency = observability.record(model, start)
            cost = estimate_cost(model, tokens)

            record_request("default", model, latency, tokens, cost)

            return {
                "model": model,
                "latency_ms": latency,
                "estimated_cost": cost,
                "tokens": tokens,
                "output": output,
                "cache": False
            }

    async def auto(self, prompt):
        # simple fallback to azure for now
        return await self.single_route("azure", prompt)

    async def ensemble(self, prompt):
        async with semaphore:
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

            best_model = max(results, key=lambda m: len(results[m]))

            return {
                "selected_model": best_model,
                "response": results.get(best_model),
                "all_responses": results
            }
