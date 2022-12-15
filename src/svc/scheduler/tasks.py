import json

from celery_conf import celery
from core.config import app_logger
from svc.parser import FbParser
from pathlib import Path


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

            fb_parser = FbParser(json_data["Геопозиция"], json_data["Запрос"], json_data["chat_id"])
            fb_parser.start_parsing()

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

            fb_parser = FbParser(json_data["Геопозиция"], json_data["Запрос"], json_data["chat_id"])
            fb_parser.delete_non_existent_items()

            app_logger.info("Finish deleting")
            return "Done deleting"

        else:
            app_logger.info("No query and geo data to start deleting, file is empty")
            return "No input data, file is empty"

    else:
        app_logger.info("No query and geo data to start deleting, file does not exist")
        return "No input data, file does not exist"
