from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton


def get_():
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="◀ Назад",callback_data="delete_help"))

    return builder.as_markup()