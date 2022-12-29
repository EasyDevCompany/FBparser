import json
from pathlib import Path

import aiofiles
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from svc.states.states import StartState
from core.config import app_logger


async def start(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        "Для начала работы с ботом необходимо указать запрос для парсинга.\n"
        "\n"
        "Парсинг будет запускаться каждый день в 9:00 по вашему времени.\n"
        "\n"
        "После 9:00 придет либо файл, либо сообщение, что новых записей нет.\n"
        "\n"
        "Удаление несуществующих ссылок будет запускаться каждый день в 21:00 по вашему времени.\n"
        "\n"
        "Если ничего не удалилось, то никаких сообщений после 21:00 не будет."
    )
    await message.answer("Укажите запрос:")
    await state.set_state(StartState.waiting_for_query.state)


async def query_input_start(message: types.Message, state: FSMContext) -> None:
    await state.update_data(chosen_query=message.text.lower())

    user_data = await state.get_data()
    reply_dict = {"Геопозиция": 'паттайа', "Запрос": user_data["chosen_query"]}
    await message.answer(
        reply_dict,
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.finish()

    reply_dict["chat_id"] = message.chat.id

    path_to_file = Path(__file__).parent

    async with aiofiles.open(f"{path_to_file}/geo_query.json", "w", encoding="utf-8") as json_file:
        await json_file.write(json.dumps(reply_dict, ensure_ascii=False, indent=2))
    
    app_logger.info(f"Income data: {reply_dict}")


def register_handlers_start(dp: Dispatcher) -> None:
    dp.register_message_handler(start, commands="start", state="*")
    dp.register_message_handler(query_input_start, state=StartState.waiting_for_query)
