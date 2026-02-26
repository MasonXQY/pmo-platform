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
from .auth import authorize

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

    async def single_route(self, tenant, model, prompt):
        async with semaphore:
            if breaker.is_open(model):
                raise Exception(f"Circuit open for {model}")

            cached = get_cached(model, prompt)
            if cached:
                return {
                    "tenant": tenant,
                    "model": model,
                    "latency_ms": 0,
                    "estimated_cost": 0,
                    "tokens": len(cached.split()),
                    "output": cached,
                    "cache": True
                }

            request_id, start = observability.start()

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

            output = result_data["output"]
            tokens = result_data["tokens"]

            latency = observability.record(model, start)
            cost = estimate_cost(model, tokens)

            record_request(tenant, model, latency, tokens, cost)

            log_event({
                "tenant": tenant,
                "model": model,
                "latency_ms": latency,
                "tokens": tokens,
                "cost": cost
            })

            return {
                "tenant": tenant,
                "model": model,
                "latency_ms": latency,
                "estimated_cost": cost,
                "tokens": tokens,
                "output": output,
                "cache": False
            }
