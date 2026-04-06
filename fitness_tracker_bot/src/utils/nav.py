from aiogram import types
from keyboards import get_main_menu_keyboard   

from utils import format_ru_date

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

    goal_created_at = format_ru_date(goal_data["created_at"])
    goal_deadline = format_ru_date(goal_data["deadline"])
    goal_status = goal_data["status"]

    if goal_status == 'overdue':
        caption = (
        f'🎯 <b>Цель:</b>\n'
        f'<blockquote>{goal_data["goal"]}</blockquote>\n\n'
        f'📅 <b>Поставлена:</b> {goal_created_at}\n'
        f'🔥 <b>Достичь до:</b> {goal_deadline}\n\n'
        f'<blockquote>⏰ Дедлайн просрочен</blockquote>'
    )
    
    else: 
        caption = (
            f'🎯 <b>Цель:</b>\n'
            f'<blockquote>{goal_data["goal"]}</blockquote>\n\n'
            f'📅 <b>Поставлена:</b> {goal_created_at}\n'
            f'🔥 <b>Достичь до:</b> {goal_deadline}'
        )

    await message.answer_photo(
        photo=photo_id,
        caption=caption,
        reply_markup=get_main_menu_keyboard(),
        parse_mode='HTML'
    )