from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.filters.command import CommandObject
from aiogram.utils.deep_linking import decode_payload

from aiogram.fsm.context import FSMContext
from states import ProfileForm

from utils import send_main_menu
from keyboards import get_main_reply_keyboard
from middlewares import Repository

from .profile import send_user_consent
from services import handle_friend_invite


router = Router()


@router.message(CommandStart())
async def start_cmd(message: types.Message,
                    command: CommandObject,
                    state: FSMContext,
                    repo: Repository):
    user_id = message.from_user.id
    username = message.from_user.username

    inviter_id = None
    if command.args:
        try:
            decoded = decode_payload(command.args)
        except Exception:
            decoded = command.args
        if decoded.startswith("add_"):
            inviter_id = int(decoded.split("_")[1])

    if repo.users.exists_user(user_id):
        await state.clear()

        print('Пользователь уже есть в базе данных')

        text = f'<b>👋 Добро пожаловать, {username}!</b>\n\nБуду рад тебя видеть в моем <a href="http://t.me/cube_4d">тг-канале</a>!'
        await message.answer(
            text=text,
            parse_mode='HTML',
            reply_markup=get_main_reply_keyboard()
        )

        await send_main_menu(message, repo, message.from_user.id)

        if inviter_id:
            if inviter_id != user_id:
                await handle_friend_invite(message, inviter_id, repo)

    else:
        try:
            await message.delete()
        except Exception:
            pass

        await state.set_data({"inviter_id": inviter_id})
        await send_user_consent(message, state)
        await state.set_state(ProfileForm.Consent)














