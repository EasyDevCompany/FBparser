from celery_app import celery


@celery.task
def start_parsing():
    print(2 + 2)
