from aiogram.types import Message
from aiogram import types
from keyboards import get_main_menu_keyboard   

from database import Repository

from aiogram.exceptions import TelegramBadRequest

async def send_main_menu(event: types.Message | types.CallbackQuery,
                        repo: Repository, user_id: int) -> None:
    message = event.message if isinstance(event, types.CallbackQuery) else event

    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    await message.answer('🗣: Меню')

    user_gender = repo.users.get_user_gender(user_id)

    photo_id = repo.users.paste_decoration_id(f'menu_{user_gender}')
    goal_data = repo.goals.get_latest_goal(user_id)
    caption = f'<b>🎯 Цель:</b> <blockquote>{goal_data["goal"]}</blockquote>\n\n<b>🚨 Дедлайн:</b>\n{goal_data["deadline"]}'
    await message.answer_photo(
        photo=photo_id,
        caption=caption,
        reply_markup=get_main_menu_keyboard(),
        parse_mode='HTML'
    )