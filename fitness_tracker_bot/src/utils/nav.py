from aiogram.types import Message
from keyboards import get_main_menu_keyboard   
from database import Repository


async def send_main_menu(message: Message, repo: Repository):
    await message.delete()
    await message.answer('💬: Меню')

    photo_id = repo.users.paste_decoration_id('menu')
    caption = '<b>🎯Недельный отчет:\n\nЦель:</b>\n\nКоличество тренировок:\n\n<b>Средн. Интенсивность:</b>'
    await message.answer_photo(
        photo=photo_id,
        caption=caption,
        reply_markup=get_main_menu_keyboard(),
        parse_mode='HTML'    
    )