from aiogram.fsm.state import State, StatesGroup

class WorkoutForm(StatesGroup):
    type = State()
    duration = State()
    intensity = State()
    note = State()
    verify = State()

class WorkoutHistoryForm(StatesGroup):
    history = State()
    viewing = State()
    selecting_page = State()
    selecting_edit = State()