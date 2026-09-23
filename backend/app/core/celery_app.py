"""
Celery application instance (Day 6).
Redis acts as both the message broker and the result backend so heavy
ML inference runs in worker processes instead of the HTTP request loop.

Start a worker (from the backend/ directory, venv active):
    celery -A app.core.celery_app worker --loglevel=info --pool=solo
(--pool=solo is required on Windows; use the default prefork pool on Linux.)
"""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "roadruler",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.ai_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    # Re-queue the task if a worker dies mid-inference
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    # A stuck inference should never block the queue forever
    task_time_limit=300,
    task_soft_time_limit=240,
    broker_connection_retry_on_startup=True,
)
