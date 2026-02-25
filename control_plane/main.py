from fastapi import FastAPI
from pydantic import BaseModel
from .router import Router
from .observability import observability

app = FastAPI()
router = Router()

class Request(BaseModel):
    prompt: str

@app.post("/auto")
async def auto(req: Request):
    return await router.call_model("azure", req.prompt)

@app.post("/model/{model_name}")
async def call_specific(model_name: str, req: Request):
    return await router.call_model(model_name, req.prompt)

@app.post("/test-all")
async def test_all(req: Request):
    return await router.test_all(req.prompt)

@app.get("/metrics")
def metrics():
    return observability.metrics()

@app.get("/health")
def health():
    return {"status": "ok"}
