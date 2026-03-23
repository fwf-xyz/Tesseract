from aiogram import Router, types
from aiogram.filters import Command

from aiogram.fsm.context import FSMContext
from states import ProfileForm

from utils import send_main_menu
from keyboards import get_main_reply_keyboard
from middlewares import Repository

from .profile import send_user_consent


router = Router()


@router.message(Command('start'))
async def start_cmd(message: types.Message, state: FSMContext, repo: Repository):
    user_id = message.from_user.id
    username = message.from_user.username

    if repo.users.exists_user(user_id):

        print('Пользователь уже есть в базе данных')

        text = f'<b>👋 Добро пожаловать, {username}!</b>\n\nБуду рад тебя видеть в моем <a href="http://t.me/cube_4d">тг-канале</a>!'
        await message.answer(
            text=text,
            parse_mode='HTML',
            reply_markup=get_main_reply_keyboard()
        )

        await send_main_menu(message, repo, message.from_user.id)


    else:
        await message.delete()
        await send_user_consent(message, state)
        await state.set_state(ProfileForm.Consent)




        # repo.users.add_user(user_id, username)












