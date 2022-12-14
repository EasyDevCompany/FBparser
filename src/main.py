import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types.bot_command import BotCommand
from aiogram.utils import executor

from core.config import app_logger, bot, dp
from db.db import init_db
from svc.handlers.base_handler import register_handlers_start
from svc.handlers.parsing_handler import register_handlers_change_query


def on_startup(bot: Bot, loop):
    init_db()

    register_handlers_change_query(dp)
    register_handlers_start(dp)

    commands = [
        BotCommand(command="/start", description="Начало парсинга"),
        BotCommand(command="/change_query", description="Смена запроса для парсинга"),
    ]

    loop.run_until_complete(bot.set_my_commands(commands))
    app_logger.info("Bot is running")


def on_shutdown(dp: Dispatcher, loop):
    loop.run_until_complete(dp.storage.close())
    loop.run_until_complete(dp.storage.wait_closed())


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    executor.start_polling(
        dp, loop=loop, skip_updates=True, on_startup=on_startup(bot, loop), on_shutdown=on_shutdown(dp, loop)
    )
    app_logger.info("Bot was stopped")
