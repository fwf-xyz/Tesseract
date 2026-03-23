from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def history_goals_keyboard(current_page: int = 0, total_pages: int = 1) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    nav_count = 0

    if current_page > 0:
        builder.button(text='◀ Назад', callback_data='page_goals:prev')
        nav_count += 1
    if current_page < total_pages - 1:
        builder.button(text='Вперёд ▶', callback_data='page_goals:next')
        nav_count += 1
    if total_pages > 1:
        builder.button(text='⚡️ Быстрый выбор страницы', callback_data='select_page_goals')
    builder.button(text='🎯 Сменить цель', callback_data='change_goal')
    builder.button(text='× Закрыть', callback_data='close_goals')

    if nav_count:
        builder.adjust(nav_count, 1, 1, 1)
    else:
        builder.adjust(1, 1)

    return builder.as_markup()


def set_goal_status_keyboard():
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text='🟢 Выполнена',
    callback_data='goal_status_completed'))
    builder.add(InlineKeyboardButton(text='🟠 Выполнена частично',
    callback_data='goal_status_partially_completed'))
    builder.add(InlineKeyboardButton(text='🔴 НЕ выполнена',
    callback_data='goal_status_failed'))

    builder.adjust(1, 1, 1)
    return builder.as_markup()
