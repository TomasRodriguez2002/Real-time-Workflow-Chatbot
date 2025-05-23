from celery import Celery

import os
from dotenv import load_dotenv

load_dotenv()

celery_app = Celery(
    'tasks',
    broker=os.getenv('CELERY_BROKER_URL'), # redis://redis:6379/0
    backend=os.getenv('CELERY_RESULT_BACKEND') # redis://redis:6379/0
)

celery_app.conf.update(
    task_routes={
        'celery_tasks.tasks.*': {'queue': 'celery'},
    },
)
celery_app.autodiscover_tasks(["celery_tasks"])