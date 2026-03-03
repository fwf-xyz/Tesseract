from aiogram.types import Message
from keyboards import get_settings_inline_keyboard
from database import paste_decoration_id
import sqlite3


async def send_main_menu(message: Message, db: sqlite3.Connection):
    photo_id = paste_decoration_id('menu', db)

    await message.delete()
    await message.answer('💬: Меню')

    await message.answer_photo(
        photo=photo_id,
        caption= 'Цель на неделю: \n \n ⭐Средн. Интенсивность:',
        reply_markup=get_settings_inline_keyboard()    
    )