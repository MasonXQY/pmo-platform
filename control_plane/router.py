import asyncio
from .agents import KimiAgent, ClaudeAgent, AzureGPTAgent
from .observability import observability
from .cost_model import estimate_cost
from .database import record_request
from .judge import Judge
from .cache import get_cached, set_cache, init_cache

BUDGET_LIMIT = 0.05

class Router:

    def __init__(self):
        self.kimi = KimiAgent()
        self.opus = ClaudeAgent("claude-opus-4-6")
        self.sonnet = ClaudeAgent("claude-sonnet-4-6")
        self.azure = AzureGPTAgent()
        self.judge = Judge()
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
            return "opus"

        length = len(prompt.split())

        if length > 120:
            return "opus"
        elif length < 15:
            return "sonnet"
        else:
            return "kimi"

    async def single_route(self, model, prompt):
        cached = get_cached(model, prompt)
        if cached:
            return {
                "model": model,
                "latency_ms": 0,
                "estimated_cost": 0,
                "tokens": len(cached.split()),
                "output": cached,
                "cache": True
            }

        request_id, start = observability.start()

        if model == "kimi":
            result = await self.kimi.run(prompt)
        elif model == "opus":
            result = await self.opus.run(prompt)
        elif model == "sonnet":
            result = await self.sonnet.run(prompt)
        elif model == "azure":
            result = await self.azure.run(prompt)
        else:
            raise ValueError("Unknown model")

        latency = observability.record(model, start)
        tokens = len(result.split())
        cost = estimate_cost(model, tokens)

        if cost > BUDGET_LIMIT:
            raise Exception(f"Cost limit exceeded: {cost}")

        record_request(model, latency, tokens, cost)
        set_cache(model, prompt, result)

        return {
            "model": model,
            "latency_ms": latency,
            "estimated_cost": cost,
            "tokens": tokens,
            "output": result,
            "cache": False
        }

    async def ensemble(self, prompt):
        tasks = {
            "kimi": asyncio.create_task(self.kimi.run(prompt)),
            "opus": asyncio.create_task(self.opus.run(prompt)),
            "sonnet": asyncio.create_task(self.sonnet.run(prompt)),
            "azure": asyncio.create_task(self.azure.run(prompt))
        }

        results = {}
        for name, task in tasks.items():
            try:
                results[name] = await task
            except Exception as e:
                results[name] = f"ERROR: {e}"

        best_model, confidence = await self.judge.evaluate(prompt, results)

        return {
            "selected_model": best_model,
            "confidence": confidence,
            "response": results.get(best_model),
            "all_responses": results
        }

    async def auto(self, prompt):
        model = self.classify(prompt)
        return await self.single_route(model, prompt)
