from aiogram.dispatcher.filters.state import State, StatesGroup


class GeoQuery(StatesGroup):
    waiting_for_geo = State()
    waiting_for_query = State()
