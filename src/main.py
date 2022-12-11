import asyncio

from aiogram import Dispatcher
from aiogram.utils import executor

from core.config import dp
from db.db import init_db
from svc.handlers.geo_query_handler import register_handlers_geo_query

register_handlers_geo_query(dp)


def on_startup():
    init_db()


async def on_shutdown(dp: Dispatcher):
    await dp.storage.close()
    await dp.storage.wait_closed()


if __name__ == "__main__":
    # TODO: add logging
    loop = asyncio.get_event_loop()
    executor.start_polling(dp, loop=loop, skip_updates=True, on_startup=on_startup(), on_shutdown=on_shutdown(dp=dp))
