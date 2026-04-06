from datetime import date, datetime

from aiogram import types, Router, F

from aiogram.fsm.context import FSMContext
from states import StatsForm

from services import get_ai_analysis
from keyboards import get_stats_keyboard, cancel_ai_summary_keyboard
from utils import safe_delete_messages
from prompts import build_summary_prompt

from database import Repository

from utils import WorkoutConstants

import asyncio


router = Router()


@router.callback_query(F.data == "stats")
async def start_cmd(callback: types.CallbackQuery, state: FSMContext, repo: Repository):
    history = repo.workouts.get_history(callback.from_user.id, 7)

    if not history:
        text = (f'🥇 <b>Мотивационное ограничение:</b>\n'
                f'<blockquote>'
                f'Доступ к периодам статистики с ИИ-саммари открыт, если пользователь добавил хотя бы 1 тренировку за последнюю неделю'
                f'</blockquote>\n\n'
                f'<b>❌ За последние 7 дней тренировок нет</b>'
        )
        msg = await callback.message.answer(text=text, parse_mode='HTML')
        await asyncio.sleep(14)
        await msg.delete()
        await callback.answer()
        return

    quantity_workouts = len(history)
    avg_intensivity = round(
        sum(int(row['intensity']) for row in history) / quantity_workouts,
        1
    )

    avg_workouts_duration = round(
        sum(int(row['duration']) for row in history) / quantity_workouts,
        1
    )


    photo_id = repo.users.paste_decoration_id('stats')
    caption = ( 
                f'<b>🔽 Статистика За 7 Дней</b>\n\n'
                f'<blockquote><b>Кол-во тренировок:</b> 🏌️‍♀️{quantity_workouts}</blockquote>\n\n'
                f'<blockquote><b>📊Средние значения:</b>\n<b>Интенсивность:</b> ⚡️{avg_intensivity}/{WorkoutConstants.MAX_INTENSITY}\n<b>Длительность:</b> ⏳{avg_workouts_duration} (мин.)</blockquote>'
    )

    sent = await callback.message.answer_photo(
        photo=photo_id,
        caption=caption,
        reply_markup=get_stats_keyboard(),
        parse_mode='HTML'    
    )

    await state.set_state(StatsForm.weekly_stats)
    await state.update_data(messages_to_delete=[sent.message_id],
                            message_id=sent.message_id,
                            chat_id=sent.chat.id)
    await callback.answer()



@router.callback_query(StatsForm.weekly_stats, F.data == "ai_summary")
async def show_stats(callback: types.CallbackQuery, state: FSMContext, repo: Repository):
    await callback.answer('Генерирую аналитику... ⌛')

    user_id = callback.from_user.id

    profile = repo.profiles.get_user_profile(user_id)
    goal = repo.goals.get_latest_goal(user_id)

    created_at = datetime.strptime(goal['created_at'], '%Y-%m-%d %H:%M:%S')
    days_back = (date.today() - created_at.date()).days

    workouts = repo.workouts.get_history(user_id, days_back)

    if not workouts:
        await callback.message.answer(
            '<b>За период времени с постановки цели до сегодняшнего дня тренировок нет</b>\n\nДобавь тренировки, чтобы получить аналитику',
            parse_mode='HTML'
        )
        return

    past_summaries = repo.ai.get_ai_history(user_id, days_back)


    prompt = build_summary_prompt(profile, goal, workouts, past_summaries)
    print(prompt)

    text = await get_ai_analysis(prompt)
    sent = await callback.message.answer(
        text=f'<blockquote>{text}</blockquote>',
        reply_markup=cancel_ai_summary_keyboard(),
        parse_mode='HTML'
        )

    repo.ai.save_ai_summary(user_id, text)

    await state.update_data(messages_to_delete=[sent.message_id])




@router.callback_query(StatsForm.weekly_stats, F.data == 'close_stats')
async def cancel_history(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    safe_delete_messages(callback.bot,
                        callback.message.chat.id,
                        data['messages_to_delete'])
    await state.clear()


@router.callback_query(StatsForm.weekly_stats, F.data == 'math_stats')
async def set_new_stats_period(callback: types.CallbackQuery, state: FSMContext):

    text=(f'📅 <b>Укажи период статистики в днях:</b> ')
    sent = await callback.message.answer(text=text, parse_mode='HTML')
    
    await state.update_data(messages_to_delete=[sent.message_id])
    await state.set_state(StatsForm.another_stats)


@router.message(StatsForm.another_stats)
async def handle_new_period(message: types.Message, state: FSMContext, repo: Repository):
    data = await state.get_data()
    await safe_delete_messages(message.bot,
                        message.chat.id,
                        data['messages_to_delete'])
    await message.delete()

    if not message.text.isdigit():
        await message.answer('<b>Введи натуральное число (1, 2, ...):</b>', parse_mode='HTML')
        return
    
    days = int(message.text)
    history = repo.workouts.get_history(message.from_user.id, days)

    if not history:
        msg = await message.answer("⚠️ <b>За указанный период нет данных о тренировках</b>", parse_mode='HTML')
        await asyncio.sleep(5)
        await msg.delete()
        await state.clear()
        return

    quantity_workouts = len(history)
    avg_intensivity = round(
        sum(int(row['intensity']) for row in history) / quantity_workouts,
        1
    )

    avg_workouts_duration = round(
        sum(int(row['duration']) for row in history) / quantity_workouts,
        1
    )

    caption = ( 
                f'<b>🔽 Статистика За {days} Суток</b>\n\n'
                f'<blockquote><b>Кол-во тренировок:</b> 🏌️‍♀️{quantity_workouts}</blockquote>\n\n'
                f'<blockquote><b>📊Средние значения:</b>\n<b>Интенсивность:</b> ⚡️{avg_intensivity}/{WorkoutConstants.MAX_INTENSITY}\n<b>Длительность:</b> ⏳{avg_workouts_duration} (мин.)</blockquote>'
    )

    bot = message.bot
    sent = await bot.edit_message_caption(
        chat_id=data['chat_id'],
        message_id=data['message_id'],
        caption=caption,
        reply_markup=get_stats_keyboard(),
        parse_mode='HTML'
    )

    await state.update_data(messages_to_delete=[sent.message_id])
    await state.set_state(StatsForm.weekly_stats)

