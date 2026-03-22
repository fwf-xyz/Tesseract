from aiogram.fsm.state import State, StatesGroup


class ProfileForm(StatesGroup):
    Consent = State()
    Age = State()
    Gender = State()
    Height = State()
    Weight = State()
    HealthParams = State()
    Goal = State()
    Deadline = State()
    Complete = State()