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


class TaskExecutor(ABC):
    def __init__(self, geo: str, query: str, chat_id: int) -> None:
        self.geo = geo
        self.query = query
        self.chat_id = chat_id
        self.storage: List[Dict] = []
        self.date_today = dt.now().date()

    def start_parsing(self) -> None:
        """Функция парсинга (пока фейковая)"""
        # Менять от этой строчки
        fake_list = []
        num = randint(5, 10)

        for _ in range(num):
            number = randint(0, 10)
            fake_dict = {
                "item_link": f"https://market.yandex.ru/product--ramka-2p-jung-epd482-slonovaia-kost/1780078{number}",
                "header": f"Заголовок_{number}",
                "image": f"https://facebookmarket/item_{number},https://facebookmarket/item_{number}",
                "price": choice([None, number]),
                "info": f"{choice(['Квартира', 'Отель', 'Гараж'])}, Спален {number} туалетов {number}, {number}м2",
                "coordinates": f"{number*12345/100}, {number*12345/100}",
                "description": f"Описание_{number}",
                "owner_link": f"https://facebook/user_{number}",
            }
            fake_list.append(fake_dict)
            # До этой строчки

        app_logger.info("Market was parsed")

        self.storage = fake_list  # И поменять тут

        self.create_db_objects()
        return None

    def create_db_objects(self) -> None:
        """Создание объектов класса Marketitem из данных парсинга"""

        parsed_objects = self.storage
        count = 0

        for object in parsed_objects:

            item = MarketItem(
                item_link=object.get("item_link"),
                header=object.get("header"),
                image=object.get("image"),
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
                "image": item.image,
                "price": item.price,
                "info": item.info,
                "coordinates": item.coordinates,
                "description": item.description,
                "owner_link": item.owner_link,
            }
            result_list.append(temp_dict)

        return result_list

    def create_file(self, file_name, list_to_write) -> None:
        """Создание результирующего yaml файла"""
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
            if response.status_code != HTTPStatus.OK:
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
