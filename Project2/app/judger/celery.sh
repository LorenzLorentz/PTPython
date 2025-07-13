celery -A celery_app worker -l info -Q compile_queue -c 2 --max-tasks-per-child 20
celery -A celery_app worker -l info -Q judge_queue -c 4 --max-tasks-per-child 10