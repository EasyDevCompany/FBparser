import json
from pathlib import Path

import aiofiles
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from svc.states.states import ParseState


async def change_query_start(message: types.Message, state: FSMContext) -> None:
    await message.answer("Укажите запрос:")
    await state.set_state(ParseState.waiting_for_query.state)


async def query_input(message: types.Message, state: FSMContext) -> None:
    await state.update_data(chosen_query=message.text.lower())

    user_data = await state.get_data()

    path_to_file = Path(__file__).parent

    async with aiofiles.open(f"{path_to_file}/geo_query.json", "r+", encoding="utf-8") as json_file:
        data = await json_file.read()

    if not data:
        await message.answer("Упс, предыдущих данных нет. Задайте их командой /start")
        await state.finish()

    else:
        json_data = json.loads(data)
        json_data["Запрос"] = user_data["chosen_query"]

        async with aiofiles.open(f"{path_to_file}/geo_query.json", "w", encoding="utf-8") as json_file:
            await json_file.write(json.dumps(json_data, ensure_ascii=False, indent=2))

        json_data.pop("chat_id")
        await message.answer(
            json_data,
            reply_markup=types.ReplyKeyboardRemove(),
        )

        await state.finish()


def register_handlers_change_query(dp: Dispatcher) -> None:
    dp.register_message_handler(change_query_start, commands="change_query", state="*")
    dp.register_message_handler(query_input, state=ParseState.waiting_for_query)
