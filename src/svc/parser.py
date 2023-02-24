import asyncio
import csv
import os
from abc import ABC
from datetime import datetime as dt
from http import HTTPStatus
from random import choice, randint
from time import sleep
from typing import Dict, List

import requests

from core.config import app_logger, bot
from db.db import db_session
from db.db_models import MarketItem
from svc.parser_engine import Parser


parser = Parser()


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


class TaskExecutor(ABC):
    def __init__(self, geo: str, query: str, chat_id: int) -> None:
        self.geo = geo
        self.query = query.replace(" ", "%20")
        self.url = f'https://www.facebook.com/marketplace/112306758786227/search/?daysSinceListed=1&query={self.query}&exact=false'
        self.chat_id = chat_id
        self.storage: List[Dict] = []
        self.all_links: List[str] = []
        self.date_today = dt.now().date()

    def start_parsing(self) -> List[List[str]]:
        """Функция парсинга (пока фейковая)"""
        app_logger.info(f"{self.geo} --- {self.query}")
        self.all_links = parser.scroll_to_the_end_of_page(self.url)

        length = len(self.all_links)

        div_number = int(length / 3) + 1

        div_links = list(chunks(self.all_links, div_number))
        

        app_logger.info(f"Market scrolled, got links: {length}")
        return div_links

    def create_db_objects(self) -> None:
        """Создание объектов класса Marketitem из данных парсинга"""

        parsed_objects = self.storage
        count = 0

        for object in parsed_objects:
            # print('price ', object.get("price"))  ALL IS OKAY

            item = MarketItem(
                item_link=object.get("item_link"),
                header=object.get("header"),
                image=object.get("images"),
                price=object.get("price"),
                info=object.get("info"),
                coordinates=object.get("coordinates"),
                description=object.get("description"),
                owner_link=object.get("owner_link"),
            )

            exists = bool(MarketItem.query.filter_by(item_link=item.item_link).first())

            if not exists:
                db_session.add(item)
                db_session.commit()
                count += 1

        app_logger.info(f"Added {count} rows to database")
        self.get_created_rows()
        return None

    def get_created_rows(self) -> None:
        """Изъятие из бд записей, добавленных сегодня, для передачи в подготовительную функцию
        и дальнейшей записи в файл"""
        market_items = MarketItem.query.filter_by(created_at=self.date_today)

        formatted_list_of_db_objects = self.prepare_list_of_objects(market_items)

        if formatted_list_of_db_objects:
            file_name = f"parsed_{self.date_today}.csv"

            self.create_file(file_name, formatted_list_of_db_objects)

            app_logger.info("New data was successfully written to file")
            self.send_file_or_message(True, file_name, text="Новых объявлений нет, поищем завтра!")

        else:
            app_logger.info("No new data to write")
            self.send_file_or_message(False, "")
        return None

    def prepare_list_of_objects(self, market_items: list) -> list:
        """Подготовка бд-записей для записи в файл"""
        result_list = []

        for item in market_items:
            temp_dict = {
                "item_link": item.item_link,
                "header": item.header,
                "price": item.price,
                "info": item.info if item.info else item.header,
                "coordinates": item.coordinates,
                "description": item.description,
                "owner_link": item.owner_link,
                "image": item.image
            }
            result_list.append(temp_dict)

        return result_list

    def create_file(self, file_name, list_to_write) -> None:
        """Создание результирующего csv файла"""
        with open(file_name, "w", encoding="utf-8", newline="") as outfile:
            keys = list_to_write[0].keys()
            dict_writer = csv.DictWriter(outfile, keys, delimiter=";")
            dict_writer.writeheader()
            dict_writer.writerows(list_to_write)
        return None

    def delete_non_existent_items(self):
        """Удаление записей из бд, которые более недоступны на сайте"""
        market_items = MarketItem.query.all()
        items_to_delete = []
        count = 0

        for item in market_items:
            response = requests.get(url=item.item_link)
            if response.status_code >= 300:
                db_session.delete(item)
                db_session.commit()

                items_to_delete.append(item)
                count += 1

                sleep(10)

        app_logger.info(f"Deleted {count} rows from database")

        if items_to_delete:
            formatted_list_of_db_objects = self.prepare_list_of_objects(items_to_delete)

            file_name = "deleted_items.csv"
            self.create_file(file_name, formatted_list_of_db_objects)

            app_logger.info("Deleted data was successfully written to file")
            self.send_file_or_message(True, file_name)

        else:
            app_logger.info("No data to delete")
            self.send_file_or_message(False, "")

        return None

    def send_file_or_message(self, file_is_ready, file_name, *args, **kwargs) -> None:
        text = kwargs.get("text")
        if file_is_ready:
            asyncio.run(bot.send_document(chat_id=self.chat_id, document=open(file_name, "rb")))
            app_logger.info("File was sent")
            os.remove(file_name)
        else:
            if text:
                asyncio.run(bot.send_message(chat_id=self.chat_id, text=text))
                app_logger.info("Message without file was sent")
            else:
                app_logger.info("No need to send message")
        return None
