from datetime import datetime
import sqlite3

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from states import WorkoutForm
from keyboards import get_workout_type_keyboard, get_intensity_keyboard

router = Router()


# ШАГ 1 — точка входа
@router.callback_query(F.data == 'add_workout')
async def add_workout(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        'Выбери тип тренировки:',
        reply_markup=get_workout_type_keyboard()
    )
    await state.set_state(WorkoutForm.type)
    await callback.answer()


# ШАГ 2 — выбор типа
@router.callback_query(WorkoutForm.type, F.data.startswith('type_'))
async def choose_type(callback: types.CallbackQuery, state: FSMContext):
    workout_type = callback.data.replace('type_', '')
    await state.update_data(type=workout_type)

    await callback.message.answer('Укажи длительность в минутах (например: 45):')
    await state.set_state(WorkoutForm.duration)
    await callback.answer()


# ШАГ 3 — длительность
@router.message(WorkoutForm.duration)
async def choose_duration(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('Введи число, например: 45')
        return

    await state.update_data(duration=int(message.text))
    await message.answer(
        'Выбери интенсивность:',
        reply_markup=get_intensity_keyboard()
    )
    await state.set_state(WorkoutForm.intensity)


# ШАГ 4 — интенсивность
@router.callback_query(WorkoutForm.intensity, F.data.startswith('intensity_'))
async def choose_intensity(callback: types.CallbackQuery, state: FSMContext):
    intensity = callback.data.replace('intensity_', '')
    await state.update_data(intensity=intensity)

    await callback.message.answer(
        'Добавь заметку к тренировке\nИли отправь /skip чтобы пропустить'
    )
    await state.set_state(WorkoutForm.note)
    await callback.answer()


# ШАГ 5 — заметка + сохранение
@router.message(WorkoutForm.note)
async def add_note(message: types.Message, state: FSMContext, db: sqlite3.Connection):
    note = None if message.text == '/skip' else message.text
    data = await state.get_data()

    user_id = message.from_user.id
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor = db.cursor()
    cursor.execute(
        """INSERT INTO workouts (user_id, type, duration, intensity, note, created_at) 
        VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, data['type'], data['duration'], data['intensity'], note, created_at)
    )
    db.commit()
    await state.clear()

    await message.answer(
        f'✅ Тренировка сохранена!\n\n'
        f'👤 ID: {user_id}\n'
        f'🏋️ Тип: {data["type"]}\n'
        f'⏱ Длительность: {data["duration"]} мин\n'
        f'⚡️ Интенсивность: {data["intensity"]}\n'
        f'📝 Заметка: {note or "—"}\n'
        f'🕐 Время: {created_at}'
    )