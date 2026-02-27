from pydantic import BaseModel, Field
from uuid import UUID
from datetime import date

class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    budget: float | None = Field(None, ge=0)
    start_date: date | None = None
    end_date: date | None = None

class ProjectResponse(ProjectCreate):
    id: UUID
    tenant_id: UUID
    status: str
    health_score: float

    class Config:
        orm_mode = True
