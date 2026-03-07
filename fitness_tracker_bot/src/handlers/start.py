from aiogram import Router, types
from aiogram.filters import Command

from utils import send_main_menu
from keyboards import get_main_reply_keyboard
from middlewares import Repository


router = Router()


@router.message(Command('start'))
async def start_cmd(message: types.Message, repo: Repository):
    user_id = message.from_user.id
    username = message.from_user.username

    repo.users.add_user(user_id, username)

    text = f'<b>👋 Добро пожаловать, {username}!</b> \n \n Подпишись на мой <a href="http://t.me/cube_4d">тг-канал</a>!'
    await message.answer(
        text=text,
        parse_mode='HTML',
        reply_markup=get_main_reply_keyboard()
    )

    await send_main_menu(message, repo)










