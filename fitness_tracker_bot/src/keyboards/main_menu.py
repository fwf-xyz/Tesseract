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


def get_main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(text="💪 Добавить тренировку",callback_data="add_workout"))
    
    builder.add(InlineKeyboardButton(text="📊 История", callback_data="history"))
    builder.add(InlineKeyboardButton(text="📈 Статистика", callback_data="stats"))
    
    builder.add(InlineKeyboardButton(text="🎯 Цели", callback_data="goals"))
    builder.add(InlineKeyboardButton(text="👥 Друзья", callback_data="friends"))
    
    builder.add(InlineKeyboardButton(text="🏆 Достижения", callback_data="achievements"))

    builder.adjust(1, 2, 2, 1)
    return builder.as_markup()


def skip_note_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="➡️ Пропустить",
        callback_data="skip_note"
    ))

    return builder.as_markup()