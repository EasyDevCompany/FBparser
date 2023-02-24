import json
from pathlib import Path

from celery import group

from celery_conf import celery
from core.config import app_logger
from svc.parser import TaskExecutor
from svc.parser import parser

@celery.task(bind=True, autoretry_for=(Exception,), default_retry_delay=30, max_retries=3)
def parsing_part(self, links):
    try:
        result = parser.get_goods_data(links)
        return result
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            result = []
            print('Run out of tries :(')
            return result
        self.retry(exc=exc)


@celery.task()
def start_parsing() -> str:
    app_logger.info("Start parsing")

    file_name = "svc/handlers/geo_query.json"
    file = Path(file_name)

    if file.exists():

        with open(file_name, "r", encoding="utf-8") as json_file:
            data = json_file.read()

        if data:
            json_data = json.loads(data)

            fb_parser = TaskExecutor(json_data["Геопозиция"], json_data["Запрос"], json_data["chat_id"])

            div_links = fb_parser.start_parsing()
            group_result = group(parsing_part.s(parsing_part, links) for links in div_links)().get()

            app_logger.info("Marked was parsed")

            for result in group_result:
                fb_parser.storage += result
            
            fb_parser.create_db_objects()

            app_logger.info("Finish parsing")
            return "Done parsing"

        else:
            app_logger.info("No query and geo data to start parsing, file is empty")
            return "No input data to parse, file is empty"

    else:
        app_logger.info("No query and geo data to start parsing, file does not exist")
        return "No input data to parse, file does not exist"


@celery.task()
def delete_links() -> str:
    app_logger.info("Start deletion")

    file_name = "svc/handlers/geo_query.json"
    file = Path(file_name)

    if file.exists():

        with open(file_name, "r", encoding="utf-8") as json_file:
            data = json_file.read()

        if data:
            json_data = json.loads(data)

            fb_parser = TaskExecutor(json_data["Геопозиция"], json_data["Запрос"], json_data["chat_id"])
            fb_parser.delete_non_existent_items()

            app_logger.info("Finish deleting")
            return "Done deleting"

        else:
            app_logger.info("No query and geo data to start deleting, file is empty")
            return "No input data, file is empty"

    else:
        app_logger.info("No query and geo data to start deleting, file does not exist")
        return "No input data, file does not exist"
