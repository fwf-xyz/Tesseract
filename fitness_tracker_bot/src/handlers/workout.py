from datetime import datetime
import sqlite3

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from states import WorkoutForm
from keyboards import get_workout_type_keyboard, get_intensity_keyboard

router = Router()


@router.callback_query(F.data == 'add_workout')
async def add_workout(callback: types.CallbackQuery, state: FSMContext):

    sent = await callback.message.answer(
        'Выбери тип тренировки:',
        reply_markup=get_workout_type_keyboard()
    )

    await state.set_state(WorkoutForm.type)
    await state.update_data(type_message_id=sent.message_id)
    await callback.answer()


@router.callback_query(WorkoutForm.type, F.data.startswith('type_'))
async def choose_type(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    await callback.bot.delete_message(
        chat_id=callback.message.chat.id,
        message_id=data['type_message_id']
    )

    workout_type = callback.data.replace('type_', '')
    await state.update_data(type=workout_type)

    sent = await callback.message.answer(
        'Укажи длительность тренировки в минутах:'
    )

    await state.set_state(WorkoutForm.duration)
    await state.update_data(type_message_id=sent.message_id)
    await callback.answer()


@router.message(WorkoutForm.duration)
async def choose_duration(message: types.Message, state: FSMContext):
    data = await state.get_data()

    await message.bot.delete_message(
    chat_id=message.chat.id,
    message_id=data['type_message_id']
)

    await message.delete()

    if not message.text.isdigit():
        await message.answer('Введи число от 1 до 245 минут: ')
        return

    await state.update_data(duration=int(message.text))
    await message.answer(
        'Выбери интенсивность:',
        reply_markup=get_intensity_keyboard()
    )
    await state.set_state(WorkoutForm.intensity)


@router.callback_query(WorkoutForm.intensity, F.data.startswith('intensity_'))
async def choose_intensity(callback: types.CallbackQuery, state: FSMContext):
    intensity = callback.data.replace('intensity_', '')
    await state.update_data(intensity=intensity)

    await callback.message.answer(
        'Добавь заметку к тренировке\nИли отправь /skip чтобы пропустить'
    )
    await state.set_state(WorkoutForm.note)
    await callback.answer()


@router.message(WorkoutForm.note)
async def add_note(message: types.Message, state: FSMContext, db: sqlite3.Connection):
    note = None if message.text == '/skip' else message.text
    data = await state.get_data()

    user_id = message.from_user.id
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor = db.cursor()
    cursor.execute(
        """INSERT INTO workouts (user_id, workout_type, duration, intensity, notes, created_at) VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, data['type'], data['duration'], data['intensity'], note, created_at)
    )
    db.commit()
    await state.clear()


    await message.answer(
        f'✅ ТРЕНИРОВКА СОХРАНЕНА!\n\n'
        f'👤 ID: {user_id}\n'
        f'🏋️ Тип: {data["type"]}\n'
        f'⏱ Длительность: {data["duration"]} мин\n'
        f'⚡️ Интенсивность: {data["intensity"]}\n'
        f'📝 Заметка: {note or "—"}\n'
        f'🕐 Время: {created_at}'
    )