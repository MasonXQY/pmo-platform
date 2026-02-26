from fastapi import FastAPI, Header
from pydantic import BaseModel
from .router import Router
from .database import init_db, get_metrics, get_daily_cost
from .auth import authorize
from .status import model_status
from .sla import sla_controller
from .health_score import HealthScore
from .circuit_breaker import breaker
from .model_registry import enable_model, disable_model, registry_status
from .performance import model_win_rates

app = FastAPI()
router = Router()
health_score = HealthScore()

init_db()

class Request(BaseModel):
    prompt: str

@app.post("/auto")
async def auto(req: Request, x_api_key: str = Header(...)):
    authorize(x_api_key, "azure")
    return await router.auto(req.prompt)

@app.post("/model/{model_name}")
async def call_specific(model_name: str, req: Request, x_api_key: str = Header(...)):
    authorize(x_api_key, model_name)
    return await router.single_route(model_name, req.prompt)

@app.post("/ensemble")
async def ensemble(req: Request, x_api_key: str = Header(...)):
    authorize(x_api_key, "opus")
    return await router.ensemble(req.prompt)

@app.post("/code")
async def code(req: Request, x_api_key: str = Header(...)):
    authorize(x_api_key, "opus")
    return await router.single_route("opus", req.prompt)

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

@app.get("/leaderboard")
def leaderboard(x_api_key: str = Header(...)):
    authorize(x_api_key, "azure")
    return model_win_rates()

@app.get("/admin/models")
def list_models(x_api_key: str = Header(...)):
    authorize(x_api_key, "azure")
    return registry_status()

@app.post("/admin/enable/{model}")
def enable(model: str, x_api_key: str = Header(...)):
    authorize(x_api_key, "azure")
    enable_model(model)
    return {"model": model, "status": "enabled"}

@app.post("/admin/disable/{model}")
def disable(model: str, x_api_key: str = Header(...)):
    authorize(x_api_key, "azure")
    disable_model(model)
    return {"model": model, "status": "disabled"}

@app.get("/health")
def health():
    return {"status": "ok"}
