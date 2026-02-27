import json
import time
from app.models.job import PredictionJob
from app.ai.summary_engine import generate_executive_summary


def create_job(db, tenant_id, project_id):
    job = PredictionJob(tenant_id=tenant_id, project_id=project_id)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def run_job(db, job, project):
    job.status = "running"
    db.commit()

    start = time.time()

    result = generate_executive_summary(project)

    duration_ms = int((time.time() - start) * 1000)

    job.result = json.dumps(result)
    job.execution_duration_ms = duration_ms
    job.status = "completed"
    db.commit()
