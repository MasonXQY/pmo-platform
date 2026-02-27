import json
import time
from app.queue.celery_app import celery_app
from app.ai.summary_engine import generate_executive_summary
from app.models.job import PredictionJob
from app.models.project import Project
from app.core.database import SessionLocal

@celery_app.task
def run_prediction_job(job_id):
    db = SessionLocal()

    job = db.query(PredictionJob).filter(PredictionJob.id == job_id).first()
    if not job:
        db.close()
        return

    project = db.query(Project).filter(Project.id == job.project_id).first()
    if not project:
        job.status = "failed"
        db.commit()
        db.close()
        return

    job.status = "running"
    db.commit()

    start = time.time()

    result = generate_executive_summary(project)

    duration_ms = int((time.time() - start) * 1000)

    job.result = json.dumps(result)
    job.execution_duration_ms = duration_ms
    job.status = "completed"

    db.commit()
    db.close()
