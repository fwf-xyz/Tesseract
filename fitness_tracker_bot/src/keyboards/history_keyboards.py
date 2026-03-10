from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def history_keyboard(current_page: int = 0, total_pages: int = 1) -> InlineKeyboardMarkup:
    buttons = []

    if current_page > 0:
        buttons.append(InlineKeyboardButton(text='◀️ Назад', callback_data='page_history:prev'))

    if current_page < total_pages - 1:
        buttons.append(InlineKeyboardButton(text='Вперёд ▶️', callback_data='page_history:next'))


    return InlineKeyboardMarkup(inline_keyboard=[buttons])