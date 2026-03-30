from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton


def get_stats_keyboard():
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text='🧠 ИИ-саммари',
    callback_data='ai_summary'))
    builder.add(InlineKeyboardButton(text='📅 Изменить период статистики',
    callback_data='math_stats'))
    builder.button(text='× Закрыть', callback_data='close_stats')

    builder.adjust(1, 1, 1)
    return builder.as_markup()


def cancel_ai_summary_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text='× Закрыть', callback_data='close_stats')

    return builder.as_markup()