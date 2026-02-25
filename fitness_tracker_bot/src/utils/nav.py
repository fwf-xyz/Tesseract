from aiogram.types import Message
from keyboards import get_settings_inline_keyboard

async def send_main_menu(message: Message):
    await message.delete()
    await message.answer('💬: Меню')
    await message.answer_animation(
        animation='https://chehov-vid.ru/upload/iblock/90c/90c34ff9b507bc23672924ae7193d815.gif',
        caption= 'Цель на неделю: \n \n ⭐Средн. Интенсивность:',
        reply_markup=get_settings_inline_keyboard()    
    )