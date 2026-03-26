from datetime import datetime

from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext

from database import Repository
from states import GoalHistoryForm, ChangeGoalForm
from keyboards import history_goals_keyboard, set_goal_status_keyboard, verify_new_goal_keyboard
from utils import safe_delete_messages, DateConstants, GoalConstants, send_main_menu

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
        deadline_str = goal['deadline']

        caption += '<b>{}.</b> <blockquote>🎯 {}</blockquote>\n\n<b>Статус:</b> {}\n\n<b>Добавлена:</b> {}\n<b>⏰ Дедлайн:</b> {}\n\n'.format(
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
    await state.update_data(messages_to_delete=[sent.message_id], goals_photo_message_id=sent.message_id,)







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
async def jump_to_goals_page(message: types.Message, state: FSMContext, repo: Repository):
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

    goals_photo_id = data.get('goals_photo_message_id')
    if goals_photo_id:
        sent = await message.bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=goals_photo_id,
            caption=caption,
            reply_markup=history_goals_keyboard(current_page=new_page, total_pages=total_pages),
            parse_mode='HTML'
        )
    else:
        sent = await send_goals_message(message.bot, message.chat.id, state, repo)

    await state.update_data(messages_to_delete=[sent.message_id])



@router.callback_query(GoalHistoryForm.viewing, F.data == 'change_goal')
async def change_goal_handler(callback: types.CallbackQuery, state: FSMContext, repo: Repository):

    goal_data = repo.goals.get_latest_goal(callback.from_user.id)

    text = (
        f'<b>Обнови статус для действующей цели:</b> \n\n'
        f'<blockquote>🎯 {goal_data["goal"]}</blockquote>\n\n'
        f'<b>Добавлена:</b> {goal_data["created_at"]}\n'
        f'<b>⏰ Дедлайн:</b> {goal_data["deadline"]}'
    )
    sent = await callback.message.answer(text=text, reply_markup=set_goal_status_keyboard(), parse_mode='HTML')

    await state.update_data(messages_to_delete=[sent.message_id])
    await state.set_state(ChangeGoalForm.set_status)
    await callback.answer()


@router.callback_query(ChangeGoalForm.set_status, F.data.startswith('goal_status_'))
async def choose_new_goal(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await safe_delete_messages(callback.bot, callback.message.chat.id, data['messages_to_delete'])

    goal_status = callback.data.replace('goal_status_', '')
    await state.update_data(goal_status=goal_status)

    data = await state.get_data()
    await safe_delete_messages(callback.bot, callback.message.chat.id, data['messages_to_delete'])

    sent = await callback.message.answer(
        '<b>🎯 Установи новую цель для занятий тренировками:</b>',
        parse_mode='HTML'
    )

    await state.set_state(ChangeGoalForm.new_goal)
    await state.update_data(messages_to_delete=[sent.message_id])
    await callback.answer()


@router.message(ChangeGoalForm.new_goal)
async def choose_new_deadline(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await safe_delete_messages(message.bot, message.chat.id, data['messages_to_delete'])
    await message.delete()

    await state.update_data(new_goal=message.text)
    sent = await message.answer(text='<b>⏰ Установи дедлайн для своей цели (например: 2026-06-01):</b>', parse_mode='HTML')

    await state.set_state(ChangeGoalForm.new_deadline)
    await state.update_data(messages_to_delete=[sent.message_id])


@router.message(ChangeGoalForm.new_deadline)
async def verify_new_goal(message: types.Message, state: FSMContext, repo: Repository):
    await state.update_data(new_deadline=message.text)

    data = await state.get_data()
    await safe_delete_messages(message.bot, message.chat.id, data['messages_to_delete'])
    await message.delete()

    photo_id = repo.users.paste_decoration_id('new_goal')
    text = (
        f'<b>Проверь данные:</b>\n\n'
        f'<b>Новая цель:</b><blockquote>🎯 {data['new_goal']}</blockquote>\n\n'
        f'<b>⏰ Дедлайн:</b> {data['new_deadline']}'
    )
    sent = await message.answer_photo(
        photo=photo_id,
        caption=text,
        reply_markup=verify_new_goal_keyboard(),
        parse_mode='HTML'
    )

    await state.set_state(ChangeGoalForm.verify)
    await state.update_data(messages_to_delete=[sent.message_id])


@router.callback_query(ChangeGoalForm.verify, F.data == 'confirm_new_goal')
async def confirm_new_goal(callback: types.CallbackQuery, state: FSMContext, repo: Repository) -> None:
    data = await state.get_data()

    repo.goals.change_goal_status(callback.from_user.id, data['goal_status'])
    repo.goals.save_goal(callback.from_user.id, data['new_goal'], data['new_deadline'])
    await send_main_menu(callback, repo, callback.from_user.id)

    await callback.answer('✅ Новая цель была успешно поставлена!')
    await state.clear()


@router.callback_query(ChangeGoalForm.verify, F.data == 'cancel_new_goal')
async def cancel_new_goal(callback: types.CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await safe_delete_messages(callback.bot, callback.message.chat.id, data['messages_to_delete'])

    await callback.answer('❌ Смена цели была отменена!')

    await state.clear()
