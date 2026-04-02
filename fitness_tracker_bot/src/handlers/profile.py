from datetime import datetime

from aiogram import Router, F, types

from utils import safe_delete_messages
from keyboards import sent_consent_accept, gender_keyboard, skip_health_params, verify_profile_keyboard, get_main_reply_keyboard, view_user_profile

from middlewares import Repository

from aiogram.fsm.context import FSMContext
from utils import AgeConstants, HeightConstants, WeightConstants, ProfileConstants, DateConstants
from utils import validate_age, validate_height, validate_weight, send_main_menu, progress_bar, parse_ru_datetime

from states import ProfileForm, EditProfileForm

from services import save_user_profile, update_user_profile


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
        f'{progress_bar(0)}\n\n'  f'<b>Данные, которые собирает бот для персональных ИИ-саммари:</b>\n\n'
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
    await send_and_track(state, callback.message,
                        f'{progress_bar(12)}\n\n<b>Укажи свой возраст:</b>',
                        parse_mode='HTML')

    await state.set_state(ProfileForm.Age)
    await callback.answer()


@router.message(ProfileForm.Age)
async def choose_age(message: types.Message, state: FSMContext):
    await cleanup(message.bot, message.chat.id, state, delete_user_msg=message)

    if not validate_age(message.text):
        await send_and_track(state, message,
                            f'{progress_bar(12)}\n\n<b>Приложение доступно для людей от {AgeConstants.MIN} до {AgeConstants.MAX} лет (вкл.):</b>',
                                parse_mode='HTML')
        return

    await state.update_data(age=int(message.text))
    await send_and_track(state, message,
                        f'{progress_bar(25)}\n\n<b>Укажи свой пол:</b>',
                        reply_markup=gender_keyboard(), parse_mode='HTML')

    await state.set_state(ProfileForm.Gender)


@router.callback_query(ProfileForm.Gender, F.data.startswith('gender_'))
async def choose_gender(callback: types.CallbackQuery, state: FSMContext):
    await cleanup(callback.bot, callback.message.chat.id, state)

    gender_type = callback.data.replace('gender_', '')
    await state.update_data(gender=gender_type)

    await send_and_track(state, callback.message,
                            f'{progress_bar(37)}\n\n<b>Укажи свой рост:</b>', parse_mode='HTML')

    await state.set_state(ProfileForm.Height)
    await callback.answer()


@router.message(ProfileForm.Height)
async def choose_height(message: types.Message, state: FSMContext):
    await cleanup(message.bot, message.chat.id, state, delete_user_msg=message)

    if not validate_height(message.text):
        await send_and_track(state, message,
                            f'{progress_bar(37)}\n\n<b>Антропологически возможный рост человека: от {HeightConstants.MIN} до {HeightConstants.MAX} см</b>',
                                parse_mode='HTML')
        return

    await state.update_data(height=int(message.text))
    await send_and_track(state, message,
                            f'{progress_bar(50)}\n\n<b>Укажи свой вес:</b>', parse_mode='HTML')

    await state.set_state(ProfileForm.Weight)


@router.message(ProfileForm.Weight)
async def choose_weight(message: types.Message, state: FSMContext):
    await cleanup(message.bot, message.chat.id, state, delete_user_msg=message)

    if not validate_weight(message.text):
        await send_and_track(state, message,
                            f'{progress_bar(50)}\n\n<b>Антропологически возможный вес человека: от {WeightConstants.MIN} до {WeightConstants.MAX} кг</b>',
                                parse_mode='HTML')
        return

    await state.update_data(weight=int(message.text))
    await send_and_track(state, message,
                        f'{progress_bar(62)}\n\n<b>📝 Данные о здоровье:</b>',
                        reply_markup=skip_health_params(), parse_mode='HTML')

    await state.set_state(ProfileForm.HealthParams)


@router.callback_query(ProfileForm.HealthParams, F.data == 'skip_health_params')
async def handle_skip_health_params(callback: types.CallbackQuery, state: FSMContext):
    await cleanup(callback.bot, callback.message.chat.id, state)

    await state.update_data(health_params=None)
    await send_and_track(state, callback.message,
                            f'{progress_bar(75)}\n\n<b>🎯 Установи свою цель для занятий тренировками:</b>', parse_mode='HTML')

    await state.set_state(ProfileForm.Goal)
    await callback.answer()


@router.message(ProfileForm.HealthParams)
async def choose_health_params(message: types.Message, state: FSMContext):
    await cleanup(message.bot, message.chat.id, state, delete_user_msg=message)

    await state.update_data(health_params=message.text)
    await send_and_track(state, message,
                            f'{progress_bar(75)}\n\n<b>🎯 Установи свою цель для занятий тренировками:</b>', parse_mode='HTML')

    await state.set_state(ProfileForm.Goal)


@router.message(ProfileForm.Goal)
async def choose_goal(message: types.Message, state: FSMContext):
    await cleanup(message.bot, message.chat.id, state, delete_user_msg=message)

    await state.update_data(goal=message.text)
    await send_and_track(state, message,
                        f'{progress_bar(87)}\n\n'
                        f'<b>⏰ Установи дедлайн для своей цели:</b>\n\n'
                        f'<i>Формат: 9 марта 2026 20:10</i>',
                        parse_mode='HTML')

    await state.set_state(ProfileForm.Deadline)


@router.message(ProfileForm.Deadline)
async def choose_deadline(message: types.Message, state: FSMContext, repo: Repository):
    await cleanup(message.bot, message.chat.id, state, delete_user_msg=message)

    db_datetime = parse_ru_datetime(message.text)
    if not db_datetime:
        await send_and_track(state, message,
                            f'{progress_bar(87)}\n\n'
                            f'<b>❌ Неверный формат. Попробуй ещё раз:</b>\n\n'
                            f'<i>Пример: 9 марта 2026 20:10</i>',
                            parse_mode='HTML')
        return

    await state.update_data(deadline=db_datetime)
    data = await state.get_data()

    photo_id = repo.users.paste_decoration_id(data['gender'])

    dt_str = datetime.strptime(db_datetime, '%Y-%m-%d %H:%M:%S')
    deadline_readable = '{} {} {} {:02d}:{:02d}'.format(
        dt_str.day, DateConstants.MONTHS.get(dt_str.month), dt_str.year, dt_str.hour, dt_str.minute
    )

    text = (
        f'{progress_bar(100)}\n\n'
        f'<b>Проверь данные:</b>\n\n'
        f'<b>👨‍🦳👵 Возраст:</b> {data.get("age")} лет\n\n'
        f'<b>Пол:</b> {ProfileConstants.GENDER_TYPES.get(data.get("gender"), data.get("gender"))}\n'
        f'<b>Рост:</b> {data.get("height")} см\n'
        f'<b>Вес:</b> {data.get("weight")} кг\n\n'
        f'<b>➕ Особенности здоровья:</b>\n{data.get("health_params") or "—"}\n\n'
        f'<b>🎯 Цель:</b>\n<blockquote>{data.get("goal")}</blockquote>\n'
        f'<b>⏰ Дедлайн:</b>\n{deadline_readable}\n\n'
    )

    sent = await message.answer_photo(photo=photo_id, caption=text, reply_markup=verify_profile_keyboard(), parse_mode='HTML')
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

    await send_main_menu(callback.message, repo, callback.from_user.id)
    await state.clear()
    await callback.answer('✅ Персональный профиль создан!')


@router.callback_query(ProfileForm.Complete, F.data == 'cancel_profile')
async def cancel_save_profile(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    await safe_delete_messages(callback.bot, callback.message.chat.id, data['messages_to_delete'])

    await callback.message.answer('<b>Чтобы заново создать персональный профиль напиши команду: /start</b> \n\n<blockquote>После регистрации ты сможешь редактировать персональный профиль во вкладке: "🌌 Персональный профиль"</blockquote>', parse_mode='HTML')

    await state.clear()
    await callback.answer('❌ Создание персонального профиля было отменено')








@router.callback_query(F.data == "user_profile")
async def handle_user_profile(callback: types.CallbackQuery, state: FSMContext, repo: Repository):
    data = repo.profiles.get_user_profile(callback.from_user.id)

    photo_id = repo.users.paste_decoration_id(data['gender'])
    text = (
        f'👤 <b>Твой персональный профиль:</b>\n\n'
        f'<blockquote>'
        f'🎂 <b>Возраст:</b> {data.get("age")} лет\n'
        f'⚧ <b>Пол:</b> {ProfileConstants.GENDER_TYPES.get(data.get("gender"), data.get("gender"))}\n'
        f'📏 <b>Рост:</b> {data.get("height")} см\n'
        f'⚖️ <b>Вес:</b> {data.get("weight")} кг'
        f'</blockquote>\n\n'
        f'🩺 <b>Особенности здоровья:</b>\n{data.get("health_params") or "—"}\n\n'
    )

    sent = await callback.message.answer_photo(photo=photo_id , caption=text, reply_markup=view_user_profile(), parse_mode='HTML')

    await state.update_data(messages_to_delete=[sent.message_id])
    await callback.answer()




@router.callback_query(F.data == 'edit_user_profile')
async def start_edit_profile(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await safe_delete_messages(callback.bot, callback.message.chat.id, data.get('messages_to_delete', []))

    await send_and_track(state, callback.message,
                        f'{progress_bar(12)}\n\n<b>Укажи свой возраст:</b>',
                        parse_mode='HTML')

    await state.set_state(EditProfileForm.Age)
    await callback.answer()


@router.message(EditProfileForm.Age)
async def edit_age(message: types.Message, state: FSMContext):
    await cleanup(message.bot, message.chat.id, state, delete_user_msg=message)

    if not validate_age(message.text):
        await send_and_track(state, message,
                            f'{progress_bar(12)}\n\n<b>Приложение доступно для людей от {AgeConstants.MIN} до {AgeConstants.MAX} лет (вкл.):</b>',
                            parse_mode='HTML')
        return

    await state.update_data(age=int(message.text))
    await send_and_track(state, message,
                        f'{progress_bar(25)}\n\n<b>Укажи свой пол:</b>',
                        reply_markup=gender_keyboard(), parse_mode='HTML')

    await state.set_state(EditProfileForm.Gender)


@router.callback_query(EditProfileForm.Gender, F.data.startswith('gender_'))
async def edit_gender(callback: types.CallbackQuery, state: FSMContext):
    await cleanup(callback.bot, callback.message.chat.id, state)

    await state.update_data(gender=callback.data.replace('gender_', ''))
    await send_and_track(state, callback.message,
                        f'{progress_bar(37)}\n\n<b>Укажи свой рост:</b>', parse_mode='HTML')

    await state.set_state(EditProfileForm.Height)
    await callback.answer()


@router.message(EditProfileForm.Height)
async def edit_height(message: types.Message, state: FSMContext):
    await cleanup(message.bot, message.chat.id, state, delete_user_msg=message)

    if not validate_height(message.text):
        await send_and_track(state, message,
                            f'{progress_bar(37)}\n\n<b>Антропологически возможный рост человека: от {HeightConstants.MIN} до {HeightConstants.MAX} см</b>',
                            parse_mode='HTML')
        return

    await state.update_data(height=int(message.text))
    await send_and_track(state, message,
                        f'{progress_bar(50)}\n\n<b>Укажи свой вес:</b>', parse_mode='HTML')

    await state.set_state(EditProfileForm.Weight)


@router.message(EditProfileForm.Weight)
async def edit_weight(message: types.Message, state: FSMContext):
    await cleanup(message.bot, message.chat.id, state, delete_user_msg=message)

    if not validate_weight(message.text):
        await send_and_track(state, message,
                            f'{progress_bar(50)}\n\n<b>Антропологически возможный вес человека: от {WeightConstants.MIN} до {WeightConstants.MAX} кг</b>',
                            parse_mode='HTML')
        return

    await state.update_data(weight=int(message.text))
    await send_and_track(state, message,
                        f'{progress_bar(62)}\n\n<b>📝 Данные о здоровье:</b>',
                        reply_markup=skip_health_params(), parse_mode='HTML')

    await state.set_state(EditProfileForm.HealthParams)


@router.callback_query(EditProfileForm.HealthParams, F.data == 'skip_health_params')
async def edit_skip_health_params(callback: types.CallbackQuery, state: FSMContext, repo: Repository):
    await cleanup(callback.bot, callback.message.chat.id, state)

    await state.update_data(health_params=None)
    await _show_edit_preview(callback.message, state, repo)

    await state.set_state(EditProfileForm.Complete)
    await callback.answer()


@router.message(EditProfileForm.HealthParams)
async def edit_health_params(message: types.Message, state: FSMContext, repo: Repository):
    await cleanup(message.bot, message.chat.id, state, delete_user_msg=message)

    await state.update_data(health_params=message.text)
    await _show_edit_preview(message, state, repo)

    await state.set_state(EditProfileForm.Complete)


async def _show_edit_preview(message: types.Message, state: FSMContext, repo: Repository):
    data = await state.get_data()

    photo_id = repo.users.paste_decoration_id(data['gender'])
    text = (
        f'{progress_bar(100)}\n\n'
        f'<b>Проверь обновлённые данные:</b>\n\n'
        f'<b>👨‍🦳👵 Возраст:</b> {data.get("age")} лет\n\n'
        f'<b>Пол:</b> {ProfileConstants.GENDER_TYPES.get(data.get("gender"), data.get("gender"))}\n'
        f'<b>Рост:</b> {data.get("height")} см\n'
        f'<b>Вес:</b> {data.get("weight")} кг\n\n'
        f'<b>➕ Особенности здоровья:</b>\n{data.get("health_params") or "—"}\n\n'
    )

    sent = await message.answer_photo(photo=photo_id, caption=text, reply_markup=verify_profile_keyboard(), parse_mode='HTML')
    await state.update_data(messages_to_delete=[sent.message_id])


@router.callback_query(EditProfileForm.Complete, F.data == 'confirm_profile')
async def confirm_edit_profile(callback: types.CallbackQuery, state: FSMContext, repo: Repository):
    data = await state.get_data()

    await safe_delete_messages(callback.bot, callback.message.chat.id, data['messages_to_delete'])

    await update_user_profile(repo, callback.from_user.id, data)

    await send_main_menu(callback.message, repo, callback.from_user.id)
    await state.clear()
    await callback.answer('✅ Персональный профиль обновлён!')


@router.callback_query(EditProfileForm.Complete, F.data == 'cancel_profile')
async def cancel_edit_profile(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    await safe_delete_messages(callback.bot, callback.message.chat.id, data['messages_to_delete'])
    await callback.message.answer('<b>Редактирование профиля отменено.</b>', parse_mode='HTML')

    await state.clear()
    await callback.answer('❌ Редактирование отменено')


@router.callback_query(F.data == 'close_user_profile')
async def close_user_profile(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    safe_delete_messages(callback.bot, callback.message.chat.id, data['messages_to_delete'])
    await callback.answer()
    await state.clear()