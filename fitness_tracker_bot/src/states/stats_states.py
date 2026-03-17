from aiogram.fsm.state import State, StatesGroup

class StatsForm(StatesGroup):
    weekly_stats = State()