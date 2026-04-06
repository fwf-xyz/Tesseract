from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.filters.command import CommandObject
from aiogram.utils.deep_linking import decode_payload
from aiogram.exceptions import TelegramBadRequest

from aiogram.fsm.context import FSMContext
from states import ProfileForm

from utils import send_main_menu
from keyboards import get_main_reply_keyboard
from middlewares import Repository

from .profile import send_user_consent
from services import handle_friend_invite


router = Router()


@router.message(CommandStart(deep_link=True))
async def start_cmd(message: types.Message,
                    command: CommandObject,
                    state: FSMContext,
                    repo: Repository):
    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    user_id = message.from_user.id

    if repo.users.exists_user(user_id):
        inviter_id = None
        if command.args:
            try:
                decoded = decode_payload(command.args)
            except Exception:
                decoded = command.args
        if decoded.startswith("add_"):
            inviter_id = int(decoded.split("_")[1])

        if inviter_id:
            await handle_friend_invite(message, inviter_id, repo)

    else:
        text = (
            f'<b>👋 Давай сначала познакомимся!</b>\n\n'
            f'<b>Чтобы добавлять друзей, нужно создать профиль:</b>\n'
            f'<blockquote><b>1.</b> Прими соглашение ниже 👇\n'
            f'<b>2.</b> Пройди регистрацию 📝\n'
            f'<b>3.</b> Отправь заявку дружбы снова 🤗</blockquote>'
        )
        await message.answer(text=text, parse_mode='HTML')
        await send_user_consent(message, state)
        await state.set_state(ProfileForm.Consent)
    

@router.message(CommandStart())
async def start_cmd(message: types.Message, state: FSMContext, repo: Repository):
    user_id = message.from_user.id
    username = message.from_user.username

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

    else:
        try:
            await message.delete()
        except Exception:
            pass

        await send_user_consent(message, state)
        await state.set_state(ProfileForm.Consent)


    













