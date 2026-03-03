from aiogram import Router, types
from aiogram.filters import Command
import sqlite3

from utils import send_main_menu
from keyboards import get_main_reply_keyboard


router = Router()

@router.message(Command('start'))
async def start_cmd(message: types.Message, db: sqlite3.Connection):
    cursor = db.cursor()
    user_id = message.from_user.id
    username = message.from_user.username

    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
        (user_id, username)
    )
    db.commit()

    await message.answer(
        f'<b>👋 Добро пожаловать, {username}!</b> \n \n Подпишись на мой <a href="http://t.me/cube_4d">тг-канал</a>!',
        parse_mode='HTML',
        reply_markup=get_main_reply_keyboard()
    )

    await send_main_menu(message, db)










