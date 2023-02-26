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
        "schedule": crontab(hour="9", minute="00"),
    },
    "part_parsing_1": {
        "task": "svc.scheduler.tasks.parsing_part",
        "schedule": crontab(hour="9", minute="15"),
        "args": ("1"),
    },
    "part_parsing_2": {
        "task": "svc.scheduler.tasks.parsing_part",
        "schedule": crontab(hour="9", minute="45"),
        "args": ("2"),
    },
    "part_parsing_3": {
        "task": "svc.scheduler.tasks.parsing_part",
        "schedule": crontab(hour="10", minute="15"),
        "args": ("3"),
    },
    "delete_non_existing_items_links": {
        "task": "svc.scheduler.tasks.delete_links",
        "schedule": crontab(hour="21", minute="00"),
    },
}

celery.conf.timezone = "Asia/Tomsk"

celery.autodiscover_tasks()
