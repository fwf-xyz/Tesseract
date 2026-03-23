from aiogram.types import Message
from keyboards import get_main_menu_keyboard   

from database import Repository

from aiogram.exceptions import TelegramBadRequest

async def send_main_menu(message: Message, repo: Repository, user_id: int):
    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    await message.answer('💬: Меню')

    photo_id = repo.users.paste_decoration_id('menu')
    goal_data = repo.goals.get_latest_goal(user_id)
    caption = f'<b>🎯 Цель:</b> {goal_data["goal"]}\n\n<b>⏰ Дедлайн:</b> {goal_data["deadline"]}'
    await message.answer_photo(
        photo=photo_id,
        caption=caption,
        reply_markup=get_main_menu_keyboard(),
        parse_mode='HTML'
    )