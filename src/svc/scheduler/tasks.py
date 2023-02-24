import json
from pathlib import Path

from celery import chain

from celery_conf import celery
from core.config import app_logger
from svc.parser import TaskExecutor
from svc.parser import parser
import time


OVERALL_RESULT = []
ALL_LINKS = []


@celery.task(bind=True, autoretry_for=(Exception,), default_retry_delay=30, max_retries=3)
def parsing_part(self, try_num):
    try:
            global OVERALL_RESULT
            global ALL_LINKS

            app_logger.info(f"Start part parsing number {try_num}")

            file_name = "svc/handlers/geo_query.json"
            file = Path(file_name)

            if file.exists():

                with open(file_name, "r", encoding="utf-8") as json_file:
                    data = json_file.read()

                if data:
                    json_data = json.loads(data)

                    if try_num == 1:
                        if len(ALL_LINKS) > 1:
                            parsed_data = parser.get_goods_data(ALL_LINKS[0])
                            OVERALL_RESULT += parsed_data
                            app_logger.info("Added 1st group")
                        elif len(ALL_LINKS) == 1:
                            parsed_data = parser.get_goods_data(ALL_LINKS[0])
                            OVERALL_RESULT += parsed_data
                            app_logger.info("Added 1st group and prepare file")
                            fb_parser = TaskExecutor(json_data["Геопозиция"], json_data["Запрос"], json_data["chat_id"])
                            fb_parser.storage = OVERALL_RESULT
                            fb_parser.create_db_objects()
                        else:
                            app_logger.info("Nothing to parse")
                    elif try_num == 2:
                        if len(ALL_LINKS) > 2:
                            parsed_data = parser.get_goods_data(ALL_LINKS[1])
                            OVERALL_RESULT += parsed_data
                            app_logger.info("Added 2nd group")
                        elif len(ALL_LINKS) == 2:
                            parsed_data = parser.get_goods_data(ALL_LINKS[1])
                            OVERALL_RESULT += parsed_data
                            app_logger.info("Added 2nd group and prepare file")
                            fb_parser = TaskExecutor(json_data["Геопозиция"], json_data["Запрос"], json_data["chat_id"])
                            fb_parser.storage = OVERALL_RESULT
                            fb_parser.create_db_objects()
                        else:
                            app_logger.info("Nothing to parse")
                    elif try_num == 3:
                        if len(ALL_LINKS) == 3:
                            parsed_data = parser.get_goods_data(ALL_LINKS[2])
                            OVERALL_RESULT += parsed_data
                            app_logger.info("Added 3d group and prepare file")
                            fb_parser = TaskExecutor(json_data["Геопозиция"], json_data["Запрос"], json_data["chat_id"])
                            fb_parser.storage = OVERALL_RESULT
                            fb_parser.create_db_objects()
                        else:
                            app_logger.info("Nothing to parse")
                    return "Done parsing"

                else:
                    app_logger.info("No query and geo data to start parsing, file is empty")
                    return "No input data to parse, file is empty"

            else:
                app_logger.info("No query and geo data to start parsing, file does not exist")
                return "No input data to parse, file does not exist"
    except Exception as exc:
        print(exc)
        if self.request.retries >= self.max_retries:
            print('Run out of tries :(')
        self.retry(exc=exc)


@celery.task()
def start_parsing() -> str:
    global OVERALL_RESULT
    global ALL_LINKS

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

            ALL_LINKS = div_links

            app_logger.info("Finish scrolling")
            return "Finish scrolling"

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
