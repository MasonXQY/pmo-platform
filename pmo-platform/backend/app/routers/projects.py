from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.schemas.project import ProjectCreate, ProjectResponse
from app.models.project import Project
from app.core.database import get_db
from app.ai.summary_engine import generate_executive_summary

router = APIRouter(prefix="/projects", tags=["Projects"])

# Temporary static tenant until full auth wired
def get_static_tenant():
    return UUID("00000000-0000-0000-0000-000000000001")

@router.post("/", response_model=ProjectResponse)
def create_project(project: ProjectCreate, db: Session = Depends(get_db), tenant_id: UUID = Depends(get_static_tenant)):
    db_project = Project(**project.dict(), tenant_id=tenant_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db), tenant_id: UUID = Depends(get_static_tenant)):
    return db.query(Project).filter(Project.tenant_id == tenant_id).all()

@router.get("/{project_id}/predict")
def predict_project(project_id: UUID, db: Session = Depends(get_db), tenant_id: UUID = Depends(get_static_tenant)):
    project = db.query(Project).filter(Project.id == project_id, Project.tenant_id == tenant_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return generate_executive_summary(project)
