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

    def classify(self, prompt):
        code_keywords = [
            "code", "python", "function", "class", "debug",
            "refactor", "implement", "optimize", "bug", "api",
            "algorithm", "database", "sql", "docker", "git",
            "compile", "typescript", "node", "react", "backend",
            "frontend", "fix error", "traceback", "exception"
        ]

        lower_prompt = prompt.lower()

        if any(word in lower_prompt for word in code_keywords):
            return "deep_reasoning"

        length = len(prompt.split())

        if length > 120:
            return "deep_reasoning"
        elif length < 15:
            return "fast"
        else:
            return "balanced"

    async def _call_model(self, model, prompt):
        if breaker.is_open(model):
            log_event({
                "event": "circuit_block",
                "model": model
            })
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
            log_event({
                "event": "model_failure",
                "model": model,
                "error": str(e)
            })
            raise e

    async def single_route(self, model, prompt):
        async with semaphore:
            prompt_hash = hash_prompt(prompt)

            cached = get_cached(model, prompt)
            if cached:
                log_event({
                    "event": "cache_hit",
                    "model": model,
                    "prompt_hash": prompt_hash
                })
                return {
                    "model": model,
                    "latency_ms": 0,
                    "estimated_cost": 0,
                    "tokens": len(cached.split()),
                    "output": cached,
                    "cache": True
                }

            request_id, start = observability.start()

            result_data = await self._call_model(model, prompt)

            output = result_data["output"]
            tokens = result_data["tokens"]

            latency = observability.record(model, start)
            cost = estimate_cost(model, tokens)

            if cost > BUDGET_LIMIT:
                log_event({
                    "event": "cost_exceeded",
                    "model": model,
                    "cost": cost
                })
                raise Exception(f"Cost limit exceeded: {cost}")

            record_request(model, latency, tokens, cost)
            set_cache(model, prompt, output)

            log_event({
                "event": "request_complete",
                "model": model,
                "prompt_hash": prompt_hash,
                "latency_ms": latency,
                "tokens": tokens,
                "cost": cost
            })

            return {
                "model": model,
                "latency_ms": latency,
                "estimated_cost": cost,
                "tokens": tokens,
                "output": output,
                "cache": False
            }

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

    async def auto(self, prompt):
        task_type = self.classify(prompt)
        model = self.adaptive.select_optimal(task_type)
        return await self.single_route(model, prompt)
