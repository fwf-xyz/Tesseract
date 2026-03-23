from datetime import datetime

from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext

from database import Repository
from states import GoalHistoryForm, ChangeGoalForm
from keyboards import history_goals_keyboard, set_goal_status_keyboard
from utils import safe_delete_messages, DateConstants, GoalConstants

router = Router()


ITEMS_PER_PAGE = 3

def build_goal_caption(history: list, page: int) -> str:
    total_pages = (len(history) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    start = page * ITEMS_PER_PAGE
    page_items = history[start:start + ITEMS_PER_PAGE]

    caption = '<b>📋 Мои цели:</b>\n'
    caption += '\n<i>(Страница {}/{})</i>\n\n ------------ \n'.format(page + 1, total_pages)

    for number, goal in enumerate(page_items, start=start + 1):
        dt = datetime.strptime(goal['created_at'], "%Y-%m-%d %H:%M:%S")
        date_str = "{} {} {:02d}:{:02d}".format(
            dt.day, DateConstants.MONTHS.get(dt.month), dt.hour, dt.minute
        )
        deadline_str = goal['deadline'] or '—'

        caption += '<b>{}. 🎯 {}</b>\n\n<b>Статус:</b> {}\n\n<b>Добавлена:</b> {}\n<b>⏰ Дедлайн:</b> {}\n\n'.format(
        number,
        goal['goal'],
        GoalConstants.GOAL_STATUSES.get(goal['status'], goal['status']),
        date_str,
        deadline_str,
        )
    caption += '------------\n'
    return caption


async def send_goals_message(bot, chat_id: int, state: FSMContext, repo: Repository):
    data = await state.get_data()
    history = data['history']
    current_page = data.get('current_page', 0)
    total_pages = (len(history) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    caption = build_goal_caption(history, page=current_page)
    photo_id = repo.users.paste_decoration_id('goals')

    sent = await bot.send_photo(
        chat_id=chat_id,
        photo=photo_id,
        caption=caption,
        reply_markup=history_goals_keyboard(current_page=current_page, total_pages=total_pages),
        parse_mode='HTML',
    )
    await state.update_data(messages_to_delete=[sent.message_id])







@router.callback_query(F.data == 'goals')
async def show_goals_history(callback: types.CallbackQuery, state: FSMContext, repo: Repository):
    history = repo.goals.get_goals_history(callback.from_user.id)

    await state.update_data(history=history, current_page=0)
    await state.set_state(GoalHistoryForm.viewing)

    await send_goals_message(callback.bot, callback.message.chat.id, state, repo)
    await callback.answer()


@router.callback_query(GoalHistoryForm.viewing, F.data == ('close_goals'))
async def close_handler(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    await safe_delete_messages(callback.bot, callback.message.chat.id, data.get('messages_to_delete', []))

    await state.clear()
    await callback.answer()


@router.callback_query(GoalHistoryForm.viewing, F.data.startswith('page_goals:'))
async def handle_goals_page(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split(':')[1]
    data = await state.get_data()

    history = data['history']
    page = data['current_page']
    total_pages = (len(history) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    if action == 'next' and page < total_pages - 1:
        page += 1
    elif action == 'prev' and page > 0:
        page -= 1
    else:
        await callback.answer()
        return

    await state.update_data(current_page=page)

    caption = build_goal_caption(history, page=page)
    sent = await callback.message.edit_caption(
        caption=caption,
        reply_markup=history_goals_keyboard(current_page=page, total_pages=total_pages),
        parse_mode='HTML',
    )
    await state.update_data(messages_to_delete=[sent.message_id])
    await callback.answer()


@router.callback_query(GoalHistoryForm.viewing, F.data == 'select_page_goals')
async def select_goals_page(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    total_pages = (len(data['history']) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    await state.set_state(GoalHistoryForm.selecting_page)
    sent = await callback.message.answer(
        f'⚡️<b>Введи номер страницы от 1 до {total_pages}:</b>',
        parse_mode='HTML'
    )
    await state.update_data(messages_to_delete=[sent.message_id])
    await callback.answer()


@router.message(GoalHistoryForm.selecting_page)
async def jump_to_goals_page(message: types.Message, state: FSMContext):
    data = await state.get_data()
    total_pages = (len(data['history']) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    await message.delete()
    await safe_delete_messages(message.bot, message.chat.id, data.get('messages_to_delete', []))

    if not message.text.isdigit() or not (1 <= int(message.text) <= total_pages):
        await message.answer(f"❌ Введи корректное число от 1 до {total_pages}")
        return

    new_page = int(message.text) - 1
    await state.update_data(current_page=new_page)
    await state.set_state(GoalHistoryForm.viewing)

    caption = build_goal_caption(data['history'], page=new_page)
    await message.bot.edit_message_caption(
        chat_id=message.chat.id,
        message_id=data['messages_to_delete'][0],
        caption=caption,
        reply_markup=history_goals_keyboard(current_page=new_page, total_pages=total_pages),
        parse_mode='HTML'
    )



@router.callback_query(GoalHistoryForm.viewing, F.data == 'change_goal')
async def change_goal_handler(callback: types.CallbackQuery, state: FSMContext, repo: Repository):

    goal_data = repo.goals.get_latest_goal(callback.from_user.id)

    text = (
        f'<b>Установи окончательный статус для прошлой цели:</b> \n\n'
        f'🎯 {goal_data["goal"]}\n\n'
        f'<b>Добавлена:</b> {goal_data["created_at"]}\n'
        f'<b>⏰ Дедлайн:</b> {goal_data["deadline"]}'
    )
    await callback.message.answer(text=text, reply_markup=set_goal_status_keyboard(), parse_mode='HTML')

    await state.set_state(ChangeGoalForm.set_status)
    await callback.answer()


@router.callback_query(ChangeGoalForm.set_status, F.data.startswith('goal_status_'))
async def choose_new_goal(callback: types.CallbackQuery, state: FSMContext):
    await state.upd


    data = await state.get_data()

    await safe_delete_messages(callback.bot, callback.message.chat.id, data['messages_to_delete'])

    workout_type = callback.data.replace('goal_status_', '')
    await state.update_data(type=workout_type)

    sent = await callback.message.answer(
        '⌛<b>Укажи длительность тренировки в минутах:</b>',
        parse_mode='HTML'
    )

    await state.set_state(WorkoutForm.duration)
    await state.update_data(messages_to_delete=[sent.message_id])
    await callback.answer()




#добавление даты compeleted_at цели
#меняется статус цели 













# @router.message(ProfileForm.HealthParams)
# async def choose_health_params(message: types.Message, state: FSMContext):
#     await cleanup(message.bot, message.chat.id, state, delete_user_msg=message)

#     await state.update_data(health_params=message.text)
#     await send_and_track(state, message,
#                             '<b>🎯 Установи свою цель для занятий тренировками:</b>', parse_mode='HTML')

#     await state.set_state(ProfileForm.Goal)


# @router.message(ProfileForm.Goal)
# async def choose_goal(message: types.Message, state: FSMContext):
#     await cleanup(message.bot, message.chat.id, state, delete_user_msg=message)

#     await state.update_data(goal=message.text)
#     await send_and_track(state, message,
#                             '<b>⏰ Установи дедлайн для своей цели (например: 2026-06-01):</b>', parse_mode='HTML')

#     await state.set_state(ProfileForm.Deadline)