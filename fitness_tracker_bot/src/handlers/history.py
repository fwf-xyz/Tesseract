from aiogram import types, F, Router
import sqlite3

from aiogram.fsm.context import FSMContext
from database import WorkoutRepository
from states import WorkoutHistoryForm


router = Router()


@router.callback_query(F.data == 'history')
async def show_history(callback: types.CallbackQuery, state: FSMContext):
    sent = await callback.message.answer(
        '📅 Введи временной период всех тренировок в днях:',
    )

    await state.set_state(WorkoutHistoryForm.history)
    await state.update_data(type_message_id=sent.message_id)
    await callback.answer()


@router.message(WorkoutHistoryForm.history, F.text.as_(int))
async def handle_history_input(message: types.Message, state: FSMContext,
                                db: sqlite3.Connection):
    data = await state.get_data()

    await message.bot.delete_message(
        chat_id=message.chat.id,
        message_id=data['type_message_id']
    )

    await message.delete()

    user_id = message.from_user.id
    days = int(message.text)

    repo = WorkoutRepository(db)
    history = repo.get_workout_history(user_id, days)

    if not history:
        await message.answer('За указанный период нет данных о тренировках.')
        await state.clear()
        return

    response = '📅 История тренировок за последние {} дней:\n\n'.format(days)
    for workout in history:
        response += '• {} - {} мин, {}, {}\n'.format(
            workout['workout_type'],
            workout['duration'],
            workout['intensity'],
            workout['created_at']
        )

    await message.answer(response)
    await state.clear()