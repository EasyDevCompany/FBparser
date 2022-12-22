from aiogram.dispatcher.filters.state import State, StatesGroup


class StartState(StatesGroup):
    waiting_for_query = State()


class ParseState(StatesGroup):
    waiting_for_query = State()