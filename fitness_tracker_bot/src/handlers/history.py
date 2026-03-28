from datetime import datetime
from aiogram.exceptions import TelegramBadRequest

from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext

from database import Repository

from states import WorkoutHistoryForm, EditWorkoutEntryForm
from keyboards import history_keyboard, edit_history_entry_keyboard, get_workout_type_keyboard, skip_note_keyboard, verify_workout_keyboard

from utils import safe_delete_messages, parse_ru_datetime, progress_bar
from utils import WorkoutConstants, DateConstants


router = Router()


#перенести в константы
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

    await state.update_data(messages_to_delete=[sent.message_id], history_message_id=sent.message_id)


@router.callback_query(F.data.startswith('close_'))
async def close_handler(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    messages_to_delete = data.get('messages_to_delete', [])
    if messages_to_delete:
        await safe_delete_messages(callback.bot, callback.message.chat.id, messages_to_delete)

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
            dt.day, DateConstants.MONTHS.get(dt.month), dt.hour, dt.minute
        )
        caption += '<b>{}: {} - {} мин</b>\n<i>[{}]</i>\n<b>Дата:</b> {}\n\n'.format(
            number,
            WorkoutConstants.TYPES.get(workout['workout_type'], workout['workout_type']),
            str(workout['duration']),
            f'⚡️{workout['intensity']}/{WorkoutConstants.MAX_INTENSITY}',
            date_str,
        )
    caption += '------------\n'

    return caption


@router.callback_query(F.data == 'close_history')
async def cancel_history(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    safe_delete_messages(callback.bot, callback.message.chat.id, data['messages_to_delete'])
    await callback.answer()
    await state.clear()


@router.callback_query(F.data == 'history')
async def ask_history_period(callback: types.CallbackQuery, state: FSMContext):
    sent = await callback.message.answer('📅 <b>Введи период тренировок от сегодня (в днях):</b>',
                                        parse_mode='HTML')

    await state.set_state(WorkoutHistoryForm.history)
    await state.update_data(messages_to_delete=[sent.message_id])
    await callback.answer()


@router.message(WorkoutHistoryForm.history)
async def handle_history_input(message: types.Message, state: FSMContext, repo: Repository):
    data = await state.get_data()

    await message.delete()
    await safe_delete_messages(message.bot, message.chat.id, data['messages_to_delete'])

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

    await state.update_data(messages_to_delete=[sent.message_id])

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

    await state.update_data(message_id=sent.message_id)
    await callback.answer()


@router.message(WorkoutHistoryForm.selecting_page)
async def jump_to_page(message: types.Message, state: FSMContext):
    data = await state.get_data()
    total_pages = (len(data['history']) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    
    await message.delete()

    prompt_msg_id = data.get('message_id')
    if prompt_msg_id:
        await safe_delete_messages(message.bot, message.chat.id, [prompt_msg_id])

    if not message.text.isdigit() or not (1 <= int(message.text) <= total_pages):
        await message.answer(f"❌ Введи корректное число от 1 до {total_pages}")
        return

    new_page = int(message.text) - 1
    await state.update_data(current_page=new_page)
    await state.set_state(WorkoutHistoryForm.viewing)

    caption = build_caption(data['history'], page=new_page, days=data['days'])
    
    history_message_id = data['history_message_id']
    try:
        await message.bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=history_message_id,
            caption=caption,
            reply_markup=history_keyboard(current_page=new_page, total_pages=total_pages),
            parse_mode='HTML'
        )
    except TelegramBadRequest:
        pass


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

    await state.update_data(messages_to_delete=[sent.message_id])
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

    await safe_delete_messages(message.bot, message.chat.id, data['messages_to_delete'])
    await safe_delete_messages(message.bot, message.chat.id, data['messages_to_delete'])
    await message.delete()

    dt = datetime.strptime(current_item['created_at'], "%Y-%m-%d %H:%M:%S")
    date_str = "{} {} {:02d}:{:02d}".format(
        dt.day,
        DateConstants.MONTHS.get(dt.month),
        dt.hour,
        dt.minute
    )

    photo_id = repo.users.paste_decoration_id(current_item['workout_type'])

    caption = (
    f"<b>Тип:</b> {WorkoutConstants.TYPES.get(current_item['workout_type'], current_item['workout_type'])}\n"
    f"<b>Длительность:</b> {current_item['duration']} мин\n"
    f"<b>Интенсивность:</b> ⚡️{current_item['intensity']}/{WorkoutConstants.MAX_INTENSITY}\n\n"
    f"<b>Заметка:</b> {current_item['notes'] or '—'}\n\n"
    f"<b>📅 Дата добавления:</b>\n{date_str}"
)
    sent = await message.answer_photo(
                                photo=photo_id,
                                caption=caption,
                                reply_markup=edit_history_entry_keyboard(),
                                parse_mode='HTML'
    )

    await state.update_data(messages_to_delete=[sent.message_id], editing_entry=current_item)


@router.callback_query(WorkoutHistoryForm.selecting_edit, F.data == 'back_to_history')
async def back_to_history(callback: types.CallbackQuery, state: FSMContext, repo: Repository):
    data = await state.get_data()

    await safe_delete_messages(callback.bot, callback.message.chat.id, data['messages_to_delete'])
    await state.set_state(WorkoutHistoryForm.viewing)

    await send_history_message(callback.bot, callback.message.chat.id, state, repo)

    await callback.answer()


@router.callback_query(WorkoutHistoryForm.selecting_edit, F.data == 'delete_entry')
async def delete_history_entry(callback: types.CallbackQuery, state: FSMContext, repo: Repository):
    data = await state.get_data()
    entry = data['editing_entry']

    repo.workouts.delete_entry(entry['id'])

    await safe_delete_messages(callback.bot, callback.message.chat.id, data['messages_to_delete'])
    await safe_delete_messages(callback.bot, callback.message.chat.id, [data.get('history_message_id')])
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
    





@router.callback_query(WorkoutHistoryForm.selecting_edit, F.data == 'edit_entry')
async def start_edit_entry(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await safe_delete_messages(callback.bot, callback.message.chat.id, data.get('messages_to_delete', []))

    sent = await callback.message.answer(
        f'{progress_bar(0)}\n\n<b>🏋️ Выбери тип тренировки:</b>',
        reply_markup=get_workout_type_keyboard(),
        parse_mode='HTML'
    )
    await state.update_data(messages_to_delete=[sent.message_id])
    await state.set_state(EditWorkoutEntryForm.workout_type)
    await callback.answer()


@router.callback_query(EditWorkoutEntryForm.workout_type, F.data.startswith('type_'))
async def edit_entry_workout_type(callback: types.CallbackQuery, state: FSMContext):
    await safe_delete_messages(callback.bot, callback.message.chat.id,
                                (await state.get_data()).get('messages_to_delete', []))

    await state.update_data(workout_type=callback.data.replace('type_', ''))

    sent = await callback.message.answer(
        f'{progress_bar(20)}\n\n<b>⏱ Введи длительность тренировки (мин, от {WorkoutConstants.MIN_DURATION} до {WorkoutConstants.MAX_DURATION}):</b>',
        parse_mode='HTML'
    )
    await state.update_data(messages_to_delete=[sent.message_id])
    await state.set_state(EditWorkoutEntryForm.duration)
    await callback.answer()


@router.message(EditWorkoutEntryForm.duration)
async def edit_entry_duration(message: types.Message, state: FSMContext):
    await safe_delete_messages(message.bot, message.chat.id,
                                (await state.get_data()).get('messages_to_delete', []))
    await message.delete()

    if not message.text.isdigit() or not (WorkoutConstants.MIN_DURATION <= int(message.text) <= WorkoutConstants.MAX_DURATION):
        sent = await message.answer(
            f'{progress_bar(20)}\n\n<b>Введи длительность от {WorkoutConstants.MIN_DURATION} до {WorkoutConstants.MAX_DURATION} мин:</b>',
            parse_mode='HTML'
        )
        await state.update_data(messages_to_delete=[sent.message_id])
        return

    await state.update_data(duration=int(message.text))
    sent = await message.answer(
        f'{progress_bar(40)}\n\n<b>⚡️ Введи интенсивность (от 1 до {WorkoutConstants.MAX_INTENSITY}):</b>',
        parse_mode='HTML'
    )
    await state.update_data(messages_to_delete=[sent.message_id])
    await state.set_state(EditWorkoutEntryForm.intensity)


@router.message(EditWorkoutEntryForm.intensity)
async def edit_entry_intensity(message: types.Message, state: FSMContext):
    await safe_delete_messages(message.bot, message.chat.id,
                                (await state.get_data()).get('messages_to_delete', []))
    await message.delete()

    if not message.text.isdigit() or not (1 <= int(message.text) <= WorkoutConstants.MAX_INTENSITY):
        sent = await message.answer(
            f'{progress_bar(40)}\n\n<b>Введи интенсивность от 1 до {WorkoutConstants.MAX_INTENSITY}:</b>',
            parse_mode='HTML'
        )
        await state.update_data(messages_to_delete=[sent.message_id])
        return

    await state.update_data(intensity=int(message.text))
    sent = await message.answer(
        f'{progress_bar(60)}\n\n<b>📝 Добавь заметку к тренировке:</b>',
        reply_markup=skip_note_keyboard(),
        parse_mode='HTML'
    )
    await state.update_data(messages_to_delete=[sent.message_id])
    await state.set_state(EditWorkoutEntryForm.notes)


@router.callback_query(EditWorkoutEntryForm.notes, F.data == 'skip_note')
async def edit_entry_skip_notes(callback: types.CallbackQuery, state: FSMContext):
    await safe_delete_messages(callback.bot, callback.message.chat.id,
                                (await state.get_data()).get('messages_to_delete', []))
    await state.update_data(notes=None)
    await _ask_edit_date(callback.message, state)
    await callback.answer()


@router.message(EditWorkoutEntryForm.notes)
async def edit_entry_notes(message: types.Message, state: FSMContext):
    await safe_delete_messages(message.bot, message.chat.id,
                                (await state.get_data()).get('messages_to_delete', []))
    await message.delete()
    await state.update_data(notes=message.text)
    await _ask_edit_date(message, state)


async def _ask_edit_date(message: types.Message, state: FSMContext):
    sent = await message.answer(
        f'{progress_bar(80)}\n\n'
        f'<b>📅 Введи дату и время тренировки:</b>\n\n'
        f'<i>Формат: 9 марта 2026 20:10</i>',
        parse_mode='HTML'
    )
    await state.update_data(messages_to_delete=[sent.message_id])
    await state.set_state(EditWorkoutEntryForm.date)


@router.message(EditWorkoutEntryForm.date)
async def edit_entry_date(message: types.Message, state: FSMContext, repo: Repository):
    await safe_delete_messages(message.bot, message.chat.id,
                                (await state.get_data()).get('messages_to_delete', []))
    await message.delete()

    db_datetime = parse_ru_datetime(message.text)
    if not db_datetime:
        sent = await message.answer(
            f'{progress_bar(80)}\n\n'
            f'<b>❌ Неверный формат. Попробуй ещё раз:</b>\n\n'
            f'<i>Пример: 9 марта 2026 20:10</i>',
            parse_mode='HTML'
        )
        await state.update_data(messages_to_delete=[sent.message_id])
        return

    await state.update_data(created_at=db_datetime)
    await _show_edit_entry_preview(message, state, repo)
    await state.set_state(EditWorkoutEntryForm.complete)


async def _show_edit_entry_preview(message: types.Message, state: FSMContext, repo: Repository):
    data = await state.get_data()

    dt = datetime.strptime(data['created_at'], '%Y-%m-%d %H:%M:%S')
    date_str = '{} {} {} {:02d}:{:02d}'.format(
        dt.day, DateConstants.MONTHS.get(dt.month), dt.year, dt.hour, dt.minute
    )

    photo_id = repo.users.paste_decoration_id(data['workout_type'])
    caption = (
        f'{progress_bar(100)}\n\n'
        f'<b>Проверь обновлённые данные:</b>\n\n'
        f'<b>🏋️ Тип:</b> {WorkoutConstants.TYPES.get(data["workout_type"], data["workout_type"])}\n'
        f'<b>⏱ Длительность:</b> {data["duration"]} мин\n'
        f'<b>⚡️ Интенсивность:</b> {data["intensity"]}/{WorkoutConstants.MAX_INTENSITY}\n\n'
        f'<b>📝 Заметка:</b> {data.get("notes") or "—"}\n\n'
        f'<b>📅 Дата:</b> {date_str}\n'
    )
    sent = await message.answer_photo(
        photo=photo_id,
        caption=caption,
        reply_markup=verify_workout_keyboard(),
        parse_mode='HTML'
    )
    await state.update_data(messages_to_delete=[sent.message_id])


@router.callback_query(EditWorkoutEntryForm.complete, F.data == 'confirm_workout')
async def confirm_edit_entry(callback: types.CallbackQuery, state: FSMContext, repo: Repository):
    data = await state.get_data()
    await safe_delete_messages(callback.bot, callback.message.chat.id, data['messages_to_delete'])
    await safe_delete_messages(callback.bot, callback.message.chat.id, [data.get('history_message_id')])

    repo.workouts.update_entry(
        entry_id=data['editing_entry']['id'],
        workout_type=data['workout_type'],
        duration=data['duration'],
        intensity=data['intensity'],
        notes=data.get('notes'),
        created_at=data['created_at']
    )

    history = repo.workouts.get_history(callback.from_user.id, data['days'])
    await state.update_data(history=history, current_page=data.get('current_page', 0))
    await state.set_state(WorkoutHistoryForm.viewing)

    await send_history_message(callback.bot, callback.message.chat.id, state, repo)
    await callback.answer('✅ Тренировка обновлена!')


@router.callback_query(EditWorkoutEntryForm.complete, F.data == 'cancel_workout')
async def cancel_edit_entry(callback: types.CallbackQuery, state: FSMContext, repo: Repository):
    data = await state.get_data()
    await safe_delete_messages(callback.bot, callback.message.chat.id, data['messages_to_delete'])
    await safe_delete_messages(callback.bot, callback.message.chat.id, [data.get('history_message_id')])

    await state.set_state(WorkoutHistoryForm.viewing)
    await send_history_message(callback.bot, callback.message.chat.id, state, repo)
    await callback.answer('❌ Редактирование отменено')