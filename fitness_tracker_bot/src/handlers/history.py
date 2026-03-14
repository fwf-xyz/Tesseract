from datetime import datetime

from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext

from database import Repository
from states import WorkoutHistoryForm
from keyboards import history_keyboard, edit_history_entry_keyboard
from utils import WORKOUT_TYPES, MONTHS, safe_delete_message

from config import MAX_INTENSITY_LEVEL


router = Router()

ITEMS_PER_PAGE = 5 

async def send_history_message(bot, chat_id: int, state: FSMContext, repo: Repository):
    data = await state.get_data()
    history = data['history']
    days = data['days']
    current_page = data.get('current_page', 0)
    total_pages = (len(history) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    caption = build_caption(history, page=current_page, days=days)
    photo_id = repo.users.paste_decoration_id('history')

    sent = await bot.send_photo(
        chat_id=chat_id,
        photo=photo_id,
        caption=caption,
        reply_markup=history_keyboard(current_page=current_page, total_pages=total_pages),
        parse_mode='HTML',
    )

    await state.update_data(type_message_id=sent.message_id)


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
            f'⚡️{workout['intensity']}/{MAX_INTENSITY_LEVEL}',
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

    await message.delete()
    await safe_delete_message(message.bot, message.chat.id, data['type_message_id'])

    if not message.text.isdigit():
        await message.answer('Введи натуральное число:')
        return

    days = int(message.text)
    history = repo.workouts.get_history(message.from_user.id, days)

    if not history:
        await message.answer('За указанный период нет данных о тренировках.')
        await state.clear()
        return

    await state.update_data(history=history, current_page=0, days=days)
    await state.set_state(WorkoutHistoryForm.viewing)

    await send_history_message(message.bot, message.chat.id, state, repo) 


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
        f'⚡️<b>Введи номер страницы от 1 до {total_pages}:</b>',
        parse_mode='HTML'
    )

    await state.update_data(last_ask_message_id=sent.message_id)
    await callback.answer()


@router.message(WorkoutHistoryForm.selecting_page)
async def jump_to_page(message: types.Message, state: FSMContext):
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
    data = await state.get_data()

    page = data['current_page']
    start_idx = page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE

    sent = await callback.message.answer(
        f"📝<b>Номер записи для редактирования ({start_idx + 1}-{end_idx}):</b>",
        parse_mode='HTML'
    )

    await state.update_data(last_ask_message_id=sent.message_id)
    await state.set_state(WorkoutHistoryForm.selecting_edit)
    await callback.answer()


@router.message(WorkoutHistoryForm.selecting_edit)
async def process_edit_selection(message: types.Message, state: FSMContext, repo: Repository):
    data = await state.get_data()

    history = data['history']
    page = data['current_page']

    if not message.text.isdigit():
        return await message.answer("Введи только число!")

    choice = int(message.text)
    
    start_idx = page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    current_item = history[start_idx:end_idx][(choice%ITEMS_PER_PAGE)-1]

    await safe_delete_message(message.bot, message.chat.id, data['last_ask_message_id'])
    await safe_delete_message(message.bot, message.chat.id, data['type_message_id'])
    await message.delete()

    dt = datetime.strptime(current_item['created_at'], "%Y-%m-%d %H:%M:%S")
    date_str = "{} {} {:02d}:{:02d}".format(
        dt.day,
        MONTHS.get(dt.month),
        dt.hour,
        dt.minute
    )

    photo_id = repo.users.paste_decoration_id(current_item['workout_type'])

    caption = (
    f"🏹 <b>Тип:</b> {WORKOUT_TYPES.get(current_item['workout_type'], current_item['workout_type'])}\n"
    f"⌛ <b>Длительность:</b> {current_item['duration']} мин\n"
    f"⚡️ <b>Интенсивность:</b> {current_item['intensity']}/{MAX_INTENSITY_LEVEL}\n\n"
    f"<b>Заметка:</b> {current_item['notes'] or '—'}\n\n"
    f"<b>📅 Дата добавления:</b>\n{date_str}"
)
    sent = await message.answer_photo(
                                photo=photo_id,
                                caption=caption,
                                reply_markup=edit_history_entry_keyboard(),
                                parse_mode='HTML'
    )

    await state.update_data(type_message_id=sent.message_id, editing_entry=current_item)


@router.callback_query(WorkoutHistoryForm.selecting_edit, F.data == 'back_to_history')
async def back_to_history(callback: types.CallbackQuery, state: FSMContext, repo: Repository):
    data = await state.get_data()

    await safe_delete_message(callback.bot, callback.message.chat.id, data['type_message_id'])
    await state.set_state(WorkoutHistoryForm.viewing)

    await send_history_message(callback.bot, callback.message.chat.id, state, repo)

    await callback.answer()


@router.callback_query(WorkoutHistoryForm.selecting_edit, F.data == 'delete_entry')
async def delete_history_entry(callback: types.CallbackQuery, state: FSMContext, repo: Repository):
    data = await state.get_data()
    entry = data['editing_entry']

    repo.workouts.delete_entry(entry['id'])

    await safe_delete_message(callback.bot, callback.message.chat.id, data['type_message_id'])
    await state.set_state(WorkoutHistoryForm.viewing)

    history = repo.workouts.get_history(callback.from_user.id, data['days'])

    if len(history) > 0:
        await state.update_data(history=history)
    else:
        await state.clear()
        await callback.message.answer('<b>За указанный период нет данных о тренировках.</b>'
                                    '\n\n<b>Вернись в меню и выбери другой период для просмотра истории.</b>',
                                    parse_mode='HTML'
                                    )
        return
    
    await send_history_message(callback.bot, callback.message.chat.id, state, repo)

    await callback.answer('✅Тренировка успешно удалена!',
                        show_alert=True)