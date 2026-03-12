from datetime import datetime

from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext

from database import Repository
from states import WorkoutHistoryForm
from keyboards import history_keyboard
from utils import WORKOUT_TYPES, MONTHS, safe_delete_message


router = Router()

ITEMS_PER_PAGE = 5 


@router.callback_query(F.data.startswith('close_'))
async def close_handler(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    await safe_delete_message(callback.bot, callback.message.chat.id, data['type_message_id'])

    await state.clear()
    await callback.answer()


def build_caption(history: list, page: int, days: int) -> str:
    total_pages = (len(history) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    page_items = history[start:end]

    caption = '<b>История Тренировок \nЗа {} суток:</b>\n'.format(days)
    caption += '\n<i>(Страница {}/{})</i>\n\n ------------ \n'.format(page + 1, total_pages)

    for number, workout in enumerate(page_items, start=start + 1):
        dt = datetime.strptime(workout['created_at'], "%Y-%m-%d %H:%M:%S")
        date_str = "{} {} {:02d}:{:02d}".format(
            dt.day, MONTHS.get(dt.month), dt.hour, dt.minute
        )
        caption += '<b>{}: {} - {} мин</b>\n<i>[{}]</i>\n<b>Дата:</b> {}\n\n'.format(
            number,
            WORKOUT_TYPES.get(workout['workout_type'], workout['workout_type']),
            str(workout['duration']),
            workout['intensity'],
            date_str,
        )
    caption += '------------\n'

    return caption


@router.callback_query(F.data == 'close_history')
async def cancel_history(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    safe_delete_message(callback.bot, callback.message.chat.id, data['type_message_id'])
    await state.clear()


@router.callback_query(F.data == 'history')
async def ask_history_period(callback: types.CallbackQuery, state: FSMContext):
    sent = await callback.message.answer('📅 <b>Введи период тренировок от сегодня (в днях):</b>',
                                        parse_mode='HTML')

    await state.set_state(WorkoutHistoryForm.history)
    await state.update_data(type_message_id=sent.message_id)
    await callback.answer()


@router.message(WorkoutHistoryForm.history)
async def handle_history_input(message: types.Message, state: FSMContext, repo: Repository):
    data = await state.get_data()

    await safe_delete_message(message.bot, message.chat.id, data['type_message_id'])
    await message.delete()

    if not message.text.isdigit():
        await message.answer('Введи число от 1 до 365 дней:')
        return

    days = int(message.text)
    history = repo.workouts.get_history(message.from_user.id, days)

    if not history:
        await message.answer('За указанный период нет данных о тренировках.')
        await state.clear()
        return

    total_pages = (len(history) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    await state.update_data(history=history, current_page=0, days=days)
    await state.set_state(WorkoutHistoryForm.viewing)

    caption = build_caption(history, page=0, days=days)
    photo_id = repo.users.paste_decoration_id('history')

    sent = await message.answer_photo(
        photo=photo_id,
        caption=caption,
        reply_markup=history_keyboard(current_page=0, total_pages=total_pages),
        parse_mode='HTML',
    )

    await state.update_data(type_message_id=sent.message_id)


@router.callback_query(WorkoutHistoryForm.viewing, F.data.startswith('page_history:'))
async def handle_history_page(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split(':')[1] 
    data = await state.get_data()

    history = data['history']
    days = data['days']
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

    caption = build_caption(history, page=page, days=days)
    sent = await callback.message.edit_caption(
        caption=caption,
        reply_markup=history_keyboard(current_page=page, total_pages=total_pages),
        parse_mode='HTML',
    )

    await state.update_data(type_message_id=sent.message_id)

    await callback.answer()



@router.callback_query(WorkoutHistoryForm.viewing, F.data == 'select_page_history')
async def select_history_page(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    total_pages = (len(data['history']) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    await state.set_state(WorkoutHistoryForm.selecting_page)
    
    sent = await callback.message.answer(
        f'⚡️ Введи номер страницы от 1 до {total_pages}:'
    )

    await state.update_data(last_ask_message_id=sent.message_id)
    await callback.answer()


@router.message(WorkoutHistoryForm.selecting_page)
async def jump_to_page(message: types.Message, state: FSMContext, repo: Repository):
    data = await state.get_data()
    total_pages = (len(data['history']) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    
    await message.delete()
    if 'last_ask_message_id' in data:
        await safe_delete_message(message.bot, message.chat.id, data['last_ask_message_id'])

    if not message.text.isdigit() or not (1 <= int(message.text) <= total_pages):
        await message.answer(f"❌ Введи корректное число от 1 до {total_pages}")
        return

    new_page = int(message.text) - 1
    await state.update_data(current_page=new_page)
    await state.set_state(WorkoutHistoryForm.viewing)

    caption = build_caption(data['history'], page=new_page, days=data['days'])
    await message.bot.edit_message_caption(
        chat_id=message.chat.id,
        message_id=data['type_message_id'],
        caption=caption,
        reply_markup=history_keyboard(current_page=new_page, total_pages=total_pages),
        parse_mode='HTML'
    )
        


@router.callback_query(WorkoutHistoryForm.viewing, F.data == 'edit_history')
async def start_edit_choice(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(WorkoutHistoryForm.selecting_edit)
    
    sent = await callback.message.answer(
        "📝 Введи **номер записи** из списка (1, 2, 3...), которую хочешь изменить:"
    )
    await state.update_data(last_ask_message_id=sent.message_id)
    await callback.answer()

@router.message(WorkoutHistoryForm.selecting_edit)
async def process_edit_selection(message: types.Message, state: FSMContext):
    data = await state.get_data()
    history = data['history']
    page = data['current_page']
    
    start_idx = page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    current_items = history[start_idx:end_idx]

    if not message.text.isdigit():
        return await message.answer("Введи только число!")

    choice = int(message.text)

    if not (start_idx + 1 <= choice <= start_idx + len(current_items)):
        return await message.answer(f"Выбери номер из списка выше ({start_idx + 1}-{start_idx + len(current_items)})")

    selected_workout = history[choice - 1]
    
    await message.delete()
    await safe_delete_message(message.bot, message.chat.id, data['last_ask_message_id'])

    await state.update_data(editing_workout_id=selected_workout['id']) 
    # await state.set_state(WorkoutHistoryForm.editing_confirm) # Следующий шаг...
    
    await message.answer(f"Выбрана тренировка: {selected_workout['workout_type']}. Что именно хочешь изменить?")