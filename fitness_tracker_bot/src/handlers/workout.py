from datetime import datetime

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from states import WorkoutForm
from keyboards import get_workout_type_keyboard, skip_note_keyboard, verify_workout_keyboard

from database import Repository
from utils import WORKOUT_TYPES, MONTHS, safe_delete_message
from config import MAX_INTENSITY_LEVEL


router = Router()


async def confirm_workout_data(message: types.Message, state: FSMContext,
                                note: str | None, repo: Repository) -> None:
    data = await state.get_data()

    workout_type = WORKOUT_TYPES.get(data.get('type', 'Unknown'), data.get('type', 'Unknown'))
    duration = data.get('duration', 0)
    intensity = data.get('intensity', None)

    dt = datetime.now()
    date_str = "{} {} {:02d}:{:02d}".format(
        dt.day,
        MONTHS.get(dt.month),
        dt.hour,
        dt.minute
    )

    photo_id = repo.users.paste_decoration_id('workout_saved')
    caption = (
        f'<b>Подтверждение Тренировки:</b>\n\n'
        f'🏹 <b>Тип:</b> {workout_type}\n'
        f'⌛ <b>Длительность:</b> {duration} мин\n'
        f'⚡️ <b>Интенсивность:</b> {intensity}/{MAX_INTENSITY_LEVEL}\n\n'
        f'<b>Заметка:</b> {note or "—"}\n\n'
        f'📅 <b>Дата:</b>\n{date_str}'
    )

    sent = await message.answer_photo(
        photo=photo_id,
        caption=caption,
        reply_markup=verify_workout_keyboard(),
        parse_mode='HTML'
    )

    await state.update_data(note=note, type_message_id=sent.message_id)


@router.callback_query(F.data == 'add_workout')
async def add_workout(callback: types.CallbackQuery, state: FSMContext):
    sent = await callback.message.answer(
        '<b>Выбери тип тренировки:</b>',
        reply_markup=get_workout_type_keyboard(),
        parse_mode='HTML'
    )

    await state.set_state(WorkoutForm.type)
    await state.update_data(type_message_id=sent.message_id)
    await callback.answer()


@router.callback_query(WorkoutForm.type, F.data.startswith('type_'))
async def choose_type(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    await safe_delete_message(callback.bot, callback.message.chat.id, data['type_message_id'])

    workout_type = callback.data.replace('type_', '')
    await state.update_data(type=workout_type)

    sent = await callback.message.answer(
        '⌛<b>Укажи длительность тренировки в минутах:</b>',
        parse_mode='HTML'
    )

    await state.set_state(WorkoutForm.duration)
    await state.update_data(type_message_id=sent.message_id)
    await callback.answer()


@router.message(WorkoutForm.duration)
async def choose_duration(message: types.Message, state: FSMContext):
    data = await state.get_data()

    await safe_delete_message(message.bot, message.chat.id, data['type_message_id'])
    await message.delete()

    if not message.text.isdigit() or not (1 <= int(message.text) <= 245):
        sent = await message.answer('Введи число от 1 до 245 минут: ')
        await state.update_data(type_message_id=sent.message_id)
        return

    await state.update_data(duration=int(message.text))

    sent = await message.answer(
        '<b>⚡️Укажи интенсивность тренировки от 1 до 5:</b>',
        parse_mode='HTML'
    )

    await state.set_state(WorkoutForm.intensity)
    await state.update_data(type_message_id=sent.message_id)


@router.message(WorkoutForm.intensity)
async def choose_intensity(message: types.Message, state: FSMContext):
    data = await state.get_data()

    await safe_delete_message(message.bot, message.chat.id, data['type_message_id'])
    await message.delete()

    if not message.text.isdigit() or not (1 <= int(message.text) <= 5):
        sent = await message.answer('Введи число от 1 до 5: ')
        await state.update_data(type_message_id=sent.message_id)
        return

    await state.update_data(intensity=int(message.text))

    sent = await message.answer(
        '📝<b>Добавь заметку к тренировке:</b>',
        reply_markup=skip_note_keyboard(),
        parse_mode='HTML'
    )

    await state.set_state(WorkoutForm.note)
    await state.update_data(type_message_id=sent.message_id)


@router.message(WorkoutForm.note, F.text)
async def handle_note_input(message: types.Message, state: FSMContext, repo: Repository):
    data = await state.get_data()

    await safe_delete_message(message.bot, message.chat.id, data['type_message_id'])
    await message.delete()

    await confirm_workout_data(message, state, message.text, repo)
    await state.set_state(WorkoutForm.verify)


@router.callback_query(WorkoutForm.note, F.data == 'skip_note')
async def handle_skip_note(callback: types.CallbackQuery, state: FSMContext, repo: Repository):
    data = await state.get_data()

    await safe_delete_message(callback.bot, callback.message.chat.id, data['type_message_id'])

    await confirm_workout_data(callback.message, state, None, repo)
    await state.set_state(WorkoutForm.verify)
    await callback.answer()


@router.callback_query(WorkoutForm.verify, F.data == 'confirm_workout')
async def confirm_workout(callback: types.CallbackQuery, state: FSMContext, repo: Repository) -> None:
    data = await state.get_data()

    await safe_delete_message(callback.bot, callback.message.chat.id, data['type_message_id'])

    workout_type = data.get('type', 'Unknown')
    duration = data.get('duration', 0)
    intensity = data.get('intensity', 'Normal')
    note = data.get('note')
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    repo.workouts.save_workout(callback.from_user.id, workout_type, duration, intensity, note, date_str)
    await state.clear()
    await callback.answer('✅ Запись тренировки сохранена!')


@router.callback_query(WorkoutForm.verify, F.data == 'cancel_workout')
async def cancel_workout(callback: types.CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()

    await safe_delete_message(callback.bot, callback.message.chat.id, data['type_message_id'])

    await state.clear()
    await callback.message.answer('❌ Запись тренировки отменена')
    await callback.answer()