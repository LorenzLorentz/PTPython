from celery import Celery

celery_app = Celery(
    "judge_worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["app.judger.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

celery_app.conf.task_routes = {
    'tasks.compile_task': {'queue': 'compile_queue'},
    'tasks.run_task': {'queue': 'judge_queue'},
    'tasks.collect_results_task': {'queue': 'judge_queue'},
}