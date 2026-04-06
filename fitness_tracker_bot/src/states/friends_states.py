from aiogram.fsm.state import State, StatesGroup

class FriendsHistoryForm(StatesGroup):
    viewing = State()
    add_friend = State()
    selecting_page = State()
    viewing_friend = State()