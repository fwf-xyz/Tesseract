from aiogram.types import Message
from keyboards import get_main_menu_keyboard   
from database import Repository


async def send_main_menu(message: Message, repo: Repository):
    await message.delete()
    await message.answer('💬: Меню')

    photo_id = repo.users.paste_decoration_id('menu')
    caption = (
        "<b>🎯 Цель: Похудеть на 5 кг</b>\n\n"
        "---------------------------\n"
        "<b>📋 Результаты за 7 дней:</b>\n"
        "---------------------------\n"
        "<b>Кол-во тренировок:</b> ~35\n"
        "<b>Средн. интенсивность:</b> 3–4\n"
    )
    await message.answer_photo(
        photo=photo_id,
        caption=caption,
        reply_markup=get_main_menu_keyboard(),
        parse_mode='HTML'    
    )