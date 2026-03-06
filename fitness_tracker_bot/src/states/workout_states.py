from aiogram.fsm.state import State, StatesGroup

class WorkoutForm(StatesGroup):
    type = State()
    duration = State()
    intensity = State()
    note = State()

class WorkoutHistoryForm(StatesGroup):
    history = State()