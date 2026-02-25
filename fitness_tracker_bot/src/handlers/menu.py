from aiogram import Router, F, types
#import sqlite3

from utils import send_main_menu

router = Router()

@router.message(F.text == '🏋️Меню')
async def show_menu(message: types.Message):
    await send_main_menu(message)