from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton


def get_workout_type_keyboard():
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text='🫀 Кардио',
    callback_data='type_cardio'))
    builder.add(InlineKeyboardButton(text='💪 Силовая',
    callback_data='type_strength'))
    builder.add(InlineKeyboardButton(text='🧘 Растяжка',
    callback_data='type_stretch'))

    builder.adjust(1, 1, 1)
    return builder.as_markup()


def verify_workout_keyboard():
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text='✅ Подтвердить', callback_data='confirm_workout'))
    builder.add(InlineKeyboardButton(text='❌ Отменить', callback_data='cancel_workout'))

    return builder.as_markup()


def skip_note_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="➡️ Пропустить",
        callback_data="skip_note"
    ))

    return builder.as_markup()
