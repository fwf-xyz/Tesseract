from aiogram.fsm.state import State, StatesGroup


class GoalHistoryForm(StatesGroup):
    history = State()
    viewing = State()
    selecting_page = State()


class ChangeGoalForm(StatesGroup):
    set_status = State()
    new_goal = State()
    new_deadline = State()