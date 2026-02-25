from fastapi import FastAPI, Request
from .router import Router
from .observability import observability
from .models import StandardResponse
import uuid

app = FastAPI()
router = Router()

@app.post("/auto", response_model=StandardResponse)
async def auto(request: Request):
    body = await request.json()
    prompt = body.get("prompt")

    request_id = str(uuid.uuid4())

    try:
        result = await router.auto(prompt)
        return StandardResponse(
            request_id=request_id,
            model=result.get("model"),
            latency_ms=result.get("latency_ms"),
            cost_estimate=result.get("estimated_cost"),
            output=result.get("output"),
            error=None
        )
    except Exception as e:
        return StandardResponse(
            request_id=request_id,
            model=None,
            latency_ms=None,
            cost_estimate=None,
            output=None,
            error=str(e)
        )

@app.post("/ensemble", response_model=StandardResponse)
async def ensemble(request: Request):
    body = await request.json()
    prompt = body.get("prompt")

    request_id = str(uuid.uuid4())

    try:
        result = await router.ensemble(prompt)
        return StandardResponse(
            request_id=request_id,
            model=result.get("selected_model"),
            latency_ms=None,
            cost_estimate=None,
            output=result.get("response"),
            error=None
        )
    except Exception as e:
        return StandardResponse(
            request_id=request_id,
            model=None,
            latency_ms=None,
            cost_estimate=None,
            output=None,
            error=str(e)
        )

@app.get("/metrics")
def metrics():
    return observability.metrics()

@app.get("/health")
def health():
    return {"status": "ok"}
