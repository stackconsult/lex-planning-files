"""Celery application configuration for async task processing.

Configures Celery workers for document ingestion, LexRadar processing,
and legislative monitoring with Redis broker and PostgreSQL backend.
"""
import os
from celery import Celery

from src.config.settings import settings

# Celery app with Redis broker and PostgreSQL result backend
celery_app = Celery(
    "lexcore",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "db+postgresql://"),
    include=[
        "src.workers.ingest",
        "src.workers.lexradar",
        "src.workers.monitor",
    ],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_queue="default",
    task_queues={
        "ingest": {"exchange": "ingest", "routing_key": "ingest"},
        "lexradar": {"exchange": "lexradar", "routing_key": "lexradar"},
        "monitor": {"exchange": "monitor", "routing_key": "monitor"},
    },
    task_default_exchange="default",
    task_default_routing_key="default",
)
