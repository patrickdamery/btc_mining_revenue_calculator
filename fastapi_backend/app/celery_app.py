from celery import Celery
from celery.schedules import crontab
from .config import settings

import os

CELERY_BROKER_URL = settings.CELERY_BROKER_URL
CELERY_RESULT_BACKEND = settings.CELERY_RESULT_BACKEND

celery_app = Celery(
    "worker",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)

# ensure only one task runs at a time…
celery_app.conf.update(
    worker_concurrency=1,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

celery_app.conf.beat_schedule = {
    # runs every 10 minutes
    "fetch-bitcoin-and-rate": {
        "task": "app.tasks.fetch_and_store_all",
        "schedule": 600.0,          # seconds
    },
}


# (Optional) auto-discover tasks in a "tasks" package
celery_app.autodiscover_tasks(["app.tasks"])