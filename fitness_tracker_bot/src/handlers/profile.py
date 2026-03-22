from aiogram import Router, F, types

from utils import safe_delete_messages
from keyboards import sent_consent_accept, gender_keyboard, skip_health_params, verify_profile_keyboard, get_main_reply_keyboard

from middlewares import Repository

from aiogram.fsm.context import FSMContext
from utils import AgeConstants, HeightConstants, WeightConstants, ProfileConstants, validate_age, validate_height, validate_weight, send_main_menu

from states import ProfileForm

from services import save_user_profile


router = Router()


async def cleanup(bot, chat_id: int, state: FSMContext, delete_user_msg: types.Message = None):
    data = await state.get_data()
    await safe_delete_messages(bot, chat_id, data.get('messages_to_delete', []))
    if delete_user_msg:
        await delete_user_msg.delete()


async def send_and_track(state: FSMContext, message: types.Message, text: str, **kwargs) -> types.Message:
    sent = await message.answer(text=text, **kwargs)
    await state.update_data(messages_to_delete=[sent.message_id])
    return sent

                            # state: FSMContext, repo: Repository
async def send_user_consent(message: types.Message, state: FSMContext):
    text = (
        f'<b>Данные, которые собирает бот для персональных ИИ-саммари:</b>\n\n'
        f'<b>👤 Личные:</b>\n'
        f'  • Возраст\n'
        f'  • Пол\n\n'
        f'<b>📐 Физические параметры:</b>\n'
        f'  • Рост\n'
        f'  • Вес\n\n'
        f'<b>💊 Здоровье и тренировки:</b>\n'
        f'  • Данные о здоровье\n'
        f'  • Личные заметки к тренировкам'
    )
    await send_and_track(state, message, text=text, reply_markup=sent_consent_accept(), parse_mode='HTML')




@router.callback_query(ProfileForm.Consent, F.data == 'accept_consent')
async def get_age(callback: types.CallbackQuery, state: FSMContext):
    await cleanup(callback.bot, callback.message.chat.id, state)

    await send_and_track(state, callback.message, '<b>Укажи свой возраст:</b>', parse_mode='HTML')

    await state.set_state(ProfileForm.Age)
    await callback.answer()


@router.message(ProfileForm.Age)
async def choose_age(message: types.Message, state: FSMContext):
    await cleanup(message.bot, message.chat.id, state, delete_user_msg=message)

    if not validate_age(message.text):
        await send_and_track(state, message,
                            f'<b>Приложение доступно для людей от {AgeConstants.MIN} до {AgeConstants.MAX} лет (вкл.):</b>',
                                parse_mode='HTML')
        return

    await state.update_data(age=int(message.text))
    await send_and_track(state, message, '<b>Укажи свой пол:</b>',
                            reply_markup=gender_keyboard(), parse_mode='HTML')

    await state.set_state(ProfileForm.Gender)


@router.callback_query(ProfileForm.Gender, F.data.startswith('gender_'))
async def choose_gender(callback: types.CallbackQuery, state: FSMContext):
    await cleanup(callback.bot, callback.message.chat.id, state)

    gender_type = callback.data.replace('gender_', '')
    await state.update_data(gender=gender_type)

    await send_and_track(state, callback.message,
                            '<b>Укажи свой рост:</b>', parse_mode='HTML')

    await state.set_state(ProfileForm.Height)
    await callback.answer()


@router.message(ProfileForm.Height)
async def choose_height(message: types.Message, state: FSMContext):
    await cleanup(message.bot, message.chat.id, state, delete_user_msg=message)

    if not validate_height(message.text):
        await send_and_track(state, message,
                            f'<b>Антропологически возможный рост человека: от {HeightConstants.MIN} до {HeightConstants.MAX} см</b>',
                                parse_mode='HTML')
        return

    await state.update_data(height=int(message.text))
    await send_and_track(state, message,
                            '<b>Укажи свой вес:</b>', parse_mode='HTML')

    await state.set_state(ProfileForm.Weight)


@router.message(ProfileForm.Weight)
async def choose_weight(message: types.Message, state: FSMContext):
    await cleanup(message.bot, message.chat.id, state, delete_user_msg=message)

    if not validate_weight(message.text):
        await send_and_track(state, message,
                            f'<b>Антропологически возможный вес человека: от {WeightConstants.MIN} до {WeightConstants.MAX} кг</b>',
                                parse_mode='HTML')
        return

    await state.update_data(weight=int(message.text))
    await send_and_track(state, message, '<b>📝 Данные о здоровье:</b>',
                            reply_markup=skip_health_params(), parse_mode='HTML')

    await state.set_state(ProfileForm.HealthParams)


@router.callback_query(ProfileForm.HealthParams, F.data == 'skip_health_params')
async def handle_skip_health_params(callback: types.CallbackQuery, state: FSMContext):
    await cleanup(callback.bot, callback.message.chat.id, state)

    await state.update_data(health_params=None)
    await send_and_track(state, callback.message,
                            '<b>🎯 Установи свою цель для занятий тренировками:</b>', parse_mode='HTML')

    await state.set_state(ProfileForm.Goal)
    await callback.answer()


@router.message(ProfileForm.HealthParams)
async def choose_health_params(message: types.Message, state: FSMContext):
    await cleanup(message.bot, message.chat.id, state, delete_user_msg=message)

    await state.update_data(health_params=message.text)
    await send_and_track(state, message,
                            '<b>🎯 Установи свою цель для занятий тренировками:</b>', parse_mode='HTML')

    await state.set_state(ProfileForm.Goal)


@router.message(ProfileForm.Goal)
async def choose_goal(message: types.Message, state: FSMContext):
    await cleanup(message.bot, message.chat.id, state, delete_user_msg=message)

    await state.update_data(goal=message.text)
    await send_and_track(state, message,
                            '<b>⏰ Установи дедлайн для своей цели (например: 2026-06-01):</b>', parse_mode='HTML')

    await state.set_state(ProfileForm.Deadline)


@router.message(ProfileForm.Deadline)
async def choose_deadline(message: types.Message, state: FSMContext, repo: Repository):
    await cleanup(message.bot, message.chat.id, state, delete_user_msg=message)

    await state.update_data(deadline=message.text)
    data = await state.get_data()

    photo_id = repo.users.paste_decoration_id(data['gender'])
    text = (
        f'<b>Проверь данные:</b>\n\n'
        f'<b>👨‍🦳👵 Возраст:</b> {data.get("age")} лет\n\n'
        f'<b>Пол:</b> {ProfileConstants.GENDER_TYPES.get(data.get('gender'), data.get('gender'))}\n'
        f'<b>Рост:</b> {data.get("height")} см\n'
        f'<b>Вес:</b> {data.get("weight")} кг\n\n'
        f'<b>➕ Особенности здоровья:</b>\n{data.get("health_params") or "—"}\n\n'
        f'<b>🎯 Цель:</b> {data.get("goal")}\n'
        f'<b>⏰ Дедлайн:</b> {data.get("deadline")}\n\n'
    )

    sent = await message.answer_photo(photo=photo_id , caption=text, reply_markup=verify_profile_keyboard(), parse_mode='HTML')

    await state.update_data(messages_to_delete=[sent.message_id])
    await state.set_state(ProfileForm.Complete)


@router.callback_query(ProfileForm.Complete, F.data == 'confirm_profile')
async def confirm_save_profile(callback: types.CallbackQuery, state: FSMContext, repo: Repository):
    data = await state.get_data()

    await safe_delete_messages(callback.bot, callback.message.chat.id, data['messages_to_delete'])

    user_id = callback.from_user.id
    username = callback.from_user.username

    repo.users.add_user(user_id, username)
    await save_user_profile(repo, user_id, data)
    repo.goals.save_goal(user_id, data['goal'], data['deadline'])
    text = f'<b>👋 Добро пожаловать, {username}!</b>\n\nБуду рад тебя видеть в моем <a href="http://t.me/cube_4d">тг-канале</a>!'
    await callback.message.answer(
            text=text,
            parse_mode='HTML',
            reply_markup=get_main_reply_keyboard()
        )

    await send_main_menu(callback.message, repo)
    await state.clear()
    await callback.answer('✅ Персональный профиль создан!')


@router.callback_query(ProfileForm.Complete, F.data == 'cancel_profile')
async def cancel_save_profile(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    await safe_delete_messages(callback.bot, callback.message.chat.id, data['messages_to_delete'])

    await callback.message.answer('<b>Чтобы заново создать персональный профиль напиши команду: /start \n\n(После регистрации ты сможешь редактировать персональный профиль во вкладке: "👥 Друзья"</b>)', parse_mode='HTML')

    await state.clear()
    await callback.answer('❌ Создание персонального профиля было отменено')






















# @router.callback_query(ProfileForm.HealthParams, F.data == 'skip_health_params')
# async def handle_skip_health_params(callback: types.CallbackQuery, state: FSMContext):
#     await cleanup(callback.bot, callback.message.chat.id, state)

#     await state.update_data(health_params=None)

#     await callback.message.answer(text='Добавление физиологических особенностей было пропущено')

#     await state.set_state(ProfileForm.Complete)
#     await callback.answer()


# @router.message(ProfileForm.HealthParams)
# async def choose_health_params(message: types.Message, state: FSMContext, repo: Repository):
#     await cleanup(message.bot, message.chat.id, state, delete_user_msg=message)

#     await state.update_data(health_params=message.text)

#     data = await state.get_data()
#     repo.users.add_user(message.from_user.id, message.from_user.username)
#     await save_user_profile(repo, message.from_user.id, data)
#     await message.answer(text='Профиль был успешно создан!')

#     await state.set_state(ProfileForm.Complete)






    



