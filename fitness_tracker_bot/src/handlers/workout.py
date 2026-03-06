from datetime import datetime

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from states import WorkoutForm
from keyboards import get_workout_type_keyboard, get_intensity_keyboard, skip_note_keyboard

from database import Repository


router = Router()

#можно вынести в WorkoutRepository
async def save_workout_data(note: str | None, user_id: int, message: types.Message,
                            state: FSMContext, repo: Repository) -> None:
    data = await state.get_data()
    
    workout_type = data.get('type', 'Unknown')
    duration = data.get('duration', 0)
    intensity = data.get('intensity', 'Normal')
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    repo.workouts.save_workout(user_id, workout_type, duration, intensity, note, created_at)

    await state.clear()
    
    photo_id = repo.users.paste_decoration_id('workout_saved')
    caption = (
        f'✅ <b>ТРЕНИРОВКА СОХРАНЕНА!</b>\n\n'
        f'🏹 <b>Тип:</b> {workout_type}\n'
        f'⌛ <b>Длительность:</b> {duration} мин\n'
        f'⚡️ <b>Интенсивность:</b> {intensity}\n\n'
        f'<b>Заметка:</b> {note or "—"}\n\n'
        f'📅 {created_at}'
    )

    await message.answer_photo(
        photo=photo_id,
        caption=caption,
        parse_mode='HTML'
    )


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
        '⌛ Укажи длительность тренировки в минутах:'
    )
#должно быть ограничение от 1 до 245 минут, но это можно будет добавить позже
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
        '📝 Добавь заметку к тренировке:',
        reply_markup=skip_note_keyboard()
    )
    await state.set_state(WorkoutForm.note)
    await callback.answer()


@router.message(WorkoutForm.note, F.text)
async def handle_note_input(message: types.Message, state: FSMContext, repo: Repository):
    await save_workout_data(message.text, message.from_user.id, message, state, repo)

@router.callback_query(WorkoutForm.note, F.data == 'skip_note')
async def handle_skip_note(callback: types.CallbackQuery, state: FSMContext, repo: Repository):
    await save_workout_data(None, callback.from_user.id, callback.message, state, repo)
    await callback.answer()
