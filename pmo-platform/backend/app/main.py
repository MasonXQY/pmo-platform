from fastapi import FastAPI
from app.models.base import Base
from app.core.database import engine
from app.routers import projects

app = FastAPI(title="PMO Platform")

Base.metadata.create_all(bind=engine)

app.include_router(projects.router)

@app.get("/")
def health():
    return {"status": "PMO backend running"}
