import json

from celery_conf import celery
from core.config import app_logger
from svc.parser import FbParser


@celery.task()
def start_parsing() -> str:
    app_logger.info("Start parsing")

    with open("svc/handlers/geo_query.json", "r+", encoding="utf-8") as json_file:
        data = json_file.read()

    if data:
        json_data = json.loads(data)

        fb_parser = FbParser(json_data["Геопозиция"], json_data["Запрос"], json_data["chat_id"])
        fb_parser.start_parsing()

        app_logger.info("Finish parsing")
        return "Done parsing"

    else:
        app_logger.info("No query and geo data to start parsing")
        return "No input data to parse"


@celery.task()
def delete_links() -> str:
    app_logger.info("Start deletion")

    with open("svc/handlers/geo_query.json", "r+", encoding="utf-8") as json_file:
        data = json_file.read()

    if data:
        json_data = json.loads(data)

        fb_parser = FbParser(json_data["Геопозиция"], json_data["Запрос"], json_data["chat_id"])
        fb_parser.delete_non_existent_items()

        app_logger.info("Finish deleting")
        return "Done deleting"

    else:
        app_logger.info("No query and geo data to start deleting")
        return "No input data"
