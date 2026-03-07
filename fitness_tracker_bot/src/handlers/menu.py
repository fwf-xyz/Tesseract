from aiogram import Router, F, types

from database import Repository
from utils import send_main_menu

router = Router()

@router.message(F.text == '🏋️Меню')
async def show_menu(message: types.Message, repo: Repository):
    await send_main_menu(message, repo)