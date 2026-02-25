from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from .router import Router
from .observability import observability
from .database import init_db, get_metrics
from .auth import authorize

app = FastAPI()
router = Router()

# Initialize database
init_db()

class Request(BaseModel):
    prompt: str

@app.post("/auto")
async def auto(req: Request, x_api_key: str = Header(...)):
    role = authorize(x_api_key, "azure")
    return await router.auto(req.prompt)

@app.post("/model/{model_name}")
async def call_specific(model_name: str, req: Request, x_api_key: str = Header(...)):
    role = authorize(x_api_key, model_name)
    return await router.single_route(model_name, req.prompt)

@app.post("/ensemble")
async def ensemble(req: Request, x_api_key: str = Header(...)):
    role = authorize(x_api_key, "opus")
    return await router.ensemble(req.prompt)

@app.post("/code")
async def code(req: Request, x_api_key: str = Header(...)):
    role = authorize(x_api_key, "opus")
    return await router.single_route("opus", req.prompt)

@app.get("/metrics")
def metrics(x_api_key: str = Header(...)):
    role = authorize(x_api_key, "azure")
    return get_metrics()

@app.get("/health")
def health():
    return {"status": "ok"}
