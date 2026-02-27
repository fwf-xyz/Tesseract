from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton


def get_workout_type_keyboard():
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text='🫀 Кардио',
    callback_data='type_cardio'))
    builder.add(InlineKeyboardButton(text='💪 Силовая', callback_data='type_strength'))
    builder.add(InlineKeyboardButton(text='🧘 Растяжка', callback_data='type_stretch'))

    return builder.as_markup()


def get_intensity_keyboard():
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text='🟢 Лёгкая', callback_data='intensity_low'))
    builder.add(InlineKeyboardButton(text='🟡 Средняя', callback_data='intensity_medium'))
    builder.add(InlineKeyboardButton(text='🔴 Высокая', callback_data='intensity_high'))

    return builder.as_markup()