import asyncio
from .agents import KimiAgent, ClaudeAgent, AzureGPTAgent
from .observability import observability

class Router:

    def __init__(self):
        self.kimi = KimiAgent()
        self.opus = ClaudeAgent("claude-opus-4-6")
        self.sonnet = ClaudeAgent("claude-sonnet-4-6")
        self.azure = AzureGPTAgent()

    async def call_model(self, model, prompt):
        request_id, start = observability.start()
        try:
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
            return {"model": model, "latency_ms": latency, "output": result}

        except Exception as e:
            observability.record(model, start)
            return {"model": model, "error": str(e)}

    async def test_all(self, prompt="ping"):
        tasks = {
            "kimi": asyncio.create_task(self.call_model("kimi", prompt)),
            "opus": asyncio.create_task(self.call_model("opus", prompt)),
            "sonnet": asyncio.create_task(self.call_model("sonnet", prompt)),
            "azure": asyncio.create_task(self.call_model("azure", prompt))
        }

        results = {}
        for name, task in tasks.items():
            results[name] = await task

        return results
