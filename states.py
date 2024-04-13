from aiogram.fsm.state import StatesGroup, State


class User_input(StatesGroup):
    queue_id_input = State()
    create_queue = State()
