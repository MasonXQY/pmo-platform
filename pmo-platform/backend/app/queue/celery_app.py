from celery import Celery

celery_app = Celery(
    "pmo",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

celery_app.conf.task_track_started = True
