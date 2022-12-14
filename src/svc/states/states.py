from aiogram.dispatcher.filters.state import State, StatesGroup


class StartState(StatesGroup):
    waiting_for_query = State()
    waiting_for_geo = State()


class ParseState(StatesGroup):
    waiting_for_query = State()
