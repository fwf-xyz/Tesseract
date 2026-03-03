from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import KeyboardButton, InlineKeyboardButton


def get_main_reply_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="🏋️Меню"))
    builder.add(KeyboardButton(text="💬Помощь"))

    return builder.as_markup(
        resize_keyboard=True,
        is_persistent=True
    )


def get_settings_inline_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Добавить тренировку 💪", 
        callback_data="add_workout"
    ))

    return builder.as_markup()


def skip_note_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="➡️ Пропустить",
        callback_data="skip_note"
    ))
    
    return builder.as_markup()