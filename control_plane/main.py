from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from .router import Router
from .database import init_db, get_metrics, get_daily_cost
from .auth import authorize
from .status import model_status
from .sla import sla_controller
from .health_score import HealthScore
from .circuit_breaker import breaker

app = FastAPI()
router = Router()
health_score = HealthScore()

init_db()

class PromptRequest(BaseModel):
    prompt: str

@app.post("/auto")
async def auto(req: PromptRequest, x_api_key: str = Header(...)):
    authorize(x_api_key, "azure")
    return await router.auto(req.prompt)

@app.post("/model/{model_name}")
async def call_specific(model_name: str, req: PromptRequest, x_api_key: str = Header(...)):
    authorize(x_api_key, model_name)
    return await router.single_route(model_name, req.prompt)

@app.post("/ensemble")
async def ensemble(req: PromptRequest, x_api_key: str = Header(...)):
    authorize(x_api_key, "opus")
    return await router.ensemble(req.prompt)

@app.post("/code")
async def code(req: PromptRequest, x_api_key: str = Header(...)):
    authorize(x_api_key, "opus")
    return await router.single_route("opus", req.prompt)

# ✅ OpenAI-compatible endpoint for OpenClaw
@app.post("/v1/chat/completions")
async def openai_compatible(request: Request, x_api_key: str = Header(...)):
    authorize(x_api_key, "azure")

    body = await request.json()
    messages = body.get("messages", [])
    prompt = messages[-1]["content"] if messages else ""

    result = await router.auto(prompt)

    return {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": result["output"]
                }
            }
        ]
    }

@app.get("/metrics")
def metrics(x_api_key: str = Header(...)):
    authorize(x_api_key, "azure")
    return get_metrics()

@app.get("/status")
def status(x_api_key: str = Header(...)):
    authorize(x_api_key, "azure")
    return model_status()

@app.get("/sla")
def sla(x_api_key: str = Header(...)):
    authorize(x_api_key, "azure")
    return sla_controller.evaluate()

@app.get("/health-score")
def health_score_endpoint(x_api_key: str = Header(...)):
    authorize(x_api_key, "azure")
    return health_score.evaluate()

@app.get("/cost-trend")
def cost_trend(x_api_key: str = Header(...)):
    authorize(x_api_key, "azure")
    return {
        "daily_cost": get_daily_cost(),
        "metrics": get_metrics()
    }

@app.post("/admin/disable/{model}")
def disable_model(model: str, x_api_key: str = Header(...)):
    authorize(x_api_key, "azure")
    for _ in range(5):
        breaker.record_failure(model)
    return {"model": model, "status": "disabled"}

@app.get("/health")
def health():
    return {"status": "ok"}
