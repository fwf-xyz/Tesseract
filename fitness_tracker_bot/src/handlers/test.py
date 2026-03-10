from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext

from database import Repository
from states import WorkoutHistoryForm
from keyboards import history_keyboard
from utils import WORKOUT_TYPES, INTENSITY_LEVELS, MONTHS
from datetime import datetime

router = Router()

ITEMS_PER_PAGE = 5 


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
            INTENSITY_LEVELS.get(workout['intensity'], workout['intensity']),
            date_str,
        )
    caption += '------------\n'

    return caption


@router.callback_query(F.data == 'history')
async def ask_history_period(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('📅 Введи временной период всех тренировок в днях:')
    await state.set_state(WorkoutHistoryForm.history)
    await callback.answer()


@router.message(WorkoutHistoryForm.history)
async def handle_history_input(message: types.Message, state: FSMContext, repo: Repository):
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

    await message.answer_photo(
        photo=photo_id,
        caption=caption,
        reply_markup=history_keyboard(current_page=0, total_pages=total_pages),
        parse_mode='HTML',
    )


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

    await callback.message.edit_caption(
        caption=caption,
        reply_markup=history_keyboard(current_page=page, total_pages=total_pages),
        parse_mode='HTML',
    )
    await callback.answer()