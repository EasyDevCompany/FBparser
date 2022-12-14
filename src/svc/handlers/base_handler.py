import json
from pathlib import Path

import aiofiles
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from svc.states.states import StartState


async def start(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        "Для начала работы с ботом необходимо указать геопозицию и запрос.\n"
        "Парсинг будет запускаться каждый день в 9:00 по вашему времени.\n "
        "Парсеру потребуется некоторое время, чтобы выдать результирующий файл.\n"
        "Вы можете поменять поисковый запрос в любое время командой /change_query."
    )
    await message.answer("Укажите геопозицию:")
    await state.set_state(StartState.waiting_for_geo.state)


async def geo_input_start(message: types.Message, state: FSMContext):
    await state.update_data(chosen_geo=message.text.lower())

    await state.set_state(StartState.waiting_for_query.state)
    await message.answer("Укажите запрос:")


async def query_input_start(message: types.Message, state: FSMContext) -> None:
    await state.update_data(chosen_query=message.text.lower())

    user_data = await state.get_data()
    reply_dict = {"Геопозиция": user_data["chosen_geo"], "Запрос": user_data["chosen_query"]}
    await message.answer(
        reply_dict,
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.finish()

    reply_dict["chat_id"] = message.chat.id

    path_to_file = Path(__file__).parent

    async with aiofiles.open(f"{path_to_file}/geo_query.json", "w", encoding="utf-8") as json_file:
        await json_file.write(json.dumps(reply_dict, ensure_ascii=False, indent=2))


def register_handlers_start(dp: Dispatcher) -> None:
    dp.register_message_handler(start, commands="start", state="*")
    dp.register_message_handler(geo_input_start, state=StartState.waiting_for_geo)
    dp.register_message_handler(query_input_start, state=StartState.waiting_for_query)
