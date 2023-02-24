from celery import Celery
from celery.schedules import crontab
from celery.app import trace

from core.config import config

celery = Celery(
    "periodic_parsing",
    broker=(
        f"amqp://{config.RABBITMQ_DEFAULT_USER}:{config.RABBITMQ_DEFAULT_PASS}@"
        f"{config.RABBITMQ_DEFAULT_HOST}:{config.RABBITMQ_DEFAULT_PORT}"
    ),
    backend=f'redis://{config.REDIS_HOST}:{config.REDIS_PORT}',
    include=["svc.scheduler.tasks"],
)

trace.LOG_SUCCESS = """\
    Task %(name)s[%(id)s] succeeded in %(runtime)ss\
    """

celery.conf.beat_schedule = {
    "start_parsing": {
        "task": "svc.scheduler.tasks.start_parsing",
        "schedule": crontab(hour="12", minute="05"),
    },
    "delete_non_existing_items_links": {
        "task": "svc.scheduler.tasks.delete_links",
        "schedule": crontab(hour="21"),
    },
}

celery.conf.timezone = "Asia/Tomsk"

celery.autodiscover_tasks()
