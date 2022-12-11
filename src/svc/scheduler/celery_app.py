from celery import Celery

celery = Celery(
    "periodic_parsing",
    broker=("amqp://rabbitmq:rabbitmq@localhost:5672"),
    include=["tasks"],
)

celery.conf.beat_schedule = {
    "scheduler_start_parsing": {
        "task": "scheduler.tasks.start_parsing",
        "schedule": 10,
    },
}
celery.autodiscover_tasks()
