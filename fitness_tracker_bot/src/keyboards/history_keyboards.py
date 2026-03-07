from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton


def history_keyboard():
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="⬅️",
                                    callback_data="back_slide_history"
                                    ))
    builder.add(InlineKeyboardButton(text="➡️",
                                    callback_data="next_slide_history"
                                    ))


    builder.add(InlineKeyboardButton(text="✏️ Редактировать",
                                    callback_data="edit_history"
                                    ))

    builder.adjust(2, 1)
    return builder.as_markup()