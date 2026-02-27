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

@router.post("/{project_id}/predict-async")
def predict_project_async(project_id: UUID, db: Session = Depends(get_db), tenant_id: UUID = Depends(get_static_tenant)):
    from app.models.job import PredictionJob
    from app.services.job_service import create_job
    from app.queue.tasks import run_prediction_job

    project = db.query(Project).filter(Project.id == project_id, Project.tenant_id == tenant_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    job = create_job(db, tenant_id, project_id)
    run_prediction_job.delay(str(job.id))

    return {"job_id": str(job.id), "status": job.status}

@router.get("/jobs/{job_id}")
def get_job_status(job_id: UUID, db: Session = Depends(get_db), tenant_id: UUID = Depends(get_static_tenant)):
    from app.models.job import PredictionJob

    job = db.query(PredictionJob).filter(PredictionJob.id == job_id, PredictionJob.tenant_id == tenant_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "status": job.status,
        "result": job.result,
        "execution_duration_ms": job.execution_duration_ms
    }
