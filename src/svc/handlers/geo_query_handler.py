from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from svc.states.states import GeoQuery


async def geo_query_start(message: types.Message, state: FSMContext):
    await message.answer("Укажите геопозицию:")
    await state.set_state(GeoQuery.waiting_for_geo.state)


async def geo_input(message: types.Message, state: FSMContext):
    await state.update_data(chosen_geo=message.text.lower())

    await state.set_state(GeoQuery.waiting_for_query.state)
    await message.answer("Укажите запрос:")


async def query_input(message: types.Message, state: FSMContext):
    await state.update_data(chosen_query=message.text.lower())

    user_data = await state.get_data()
    await message.answer(
        f"Геопозиция: {user_data['chosen_geo']},\n" f"Запрос: {user_data['chosen_query']}.",
        reply_markup=types.ReplyKeyboardRemove(),
    )


def register_handlers_geo_query(dp: Dispatcher):
    dp.register_message_handler(geo_query_start, commands="parse", state="*")
    dp.register_message_handler(geo_input, state=GeoQuery.waiting_for_geo)
    dp.register_message_handler(query_input, state=GeoQuery.waiting_for_query)
