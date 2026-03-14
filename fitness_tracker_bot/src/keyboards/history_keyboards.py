from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def history_keyboard(current_page: int = 0, total_pages: int = 1) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    nav_count = 0

    if current_page > 0:
        builder.button(text='◀ Назад', callback_data='page_history:prev')
        nav_count += 1
    if current_page < total_pages - 1:
        builder.button(text='Вперёд ▶', callback_data='page_history:next')
        nav_count += 1
    if total_pages > 1:
        builder.button(text='⚡️ Быстрый выбор страницы', callback_data='select_page_history')
    builder.button(text='✏️ Редактировать', callback_data='edit_history')
    builder.button(text='× Закрыть', callback_data='close_history')

    if nav_count:
        builder.adjust(nav_count, 1, 1, 1)
    else:
        builder.adjust(1, 1)

    return builder.as_markup()


def edit_history_entry_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text='✏️ Внести изменения', callback_data=f'edit_entry:entry_id')
    builder.button(text='❌ Удалить тренировку', callback_data=f'delete_entry')
    builder.button(text='◀ Назад', callback_data='back_to_history')

    builder.adjust(1, 1, 1)
    return builder.as_markup()


# entry_id: int