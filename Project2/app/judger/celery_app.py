# app/judger/celery_app.py
from celery import Celery

celery_app = Celery(
    "tasks",
    broker=config.settings.CELERY_BROKER_URL,
    backend=config.settings.CELERY_RESULT_BACKEND,
    include=["app.judger.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)