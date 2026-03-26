from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton


def get_stats_keyboard():
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text='🧠 ИИ-саммари',
    callback_data='ai_summary'))
    builder.add(InlineKeyboardButton(text='Мат статистика',
    callback_data='math_stats'))
    builder.add(InlineKeyboardButton(text='История саммари',
    callback_data='ai_history_stats'))
    builder.button(text='× Закрыть', callback_data='close_stats')

    builder.adjust(1, 2, 1)
    return builder.as_markup()


def save_ai_summary_keyboard():
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(
        text='✅ Сохранить в историю',
        callback_data='save_ai_summary')
        )
    builder.button(text='◀ Назад', callback_data='close_stats')

    builder.adjust(1, 1)
    return builder.as_markup()