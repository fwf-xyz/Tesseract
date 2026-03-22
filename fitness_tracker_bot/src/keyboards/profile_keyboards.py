from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton


def sent_consent_accept():
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="📄 Читать соглашение",callback_data="read_consent"))
    builder.add(InlineKeyboardButton(text="✅ Принимаю",callback_data="accept_consent"))

    builder.adjust(1, 1)
    return builder.as_markup()


def gender_keyboard():
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="🤵‍♂️ Мужской",callback_data="gender_man"))
    builder.add(InlineKeyboardButton(text="👱‍♀️ Женский",callback_data="gender_woman"))

    builder.adjust(2)
    return builder.as_markup()


def skip_health_params():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="➡️ Пропустить",
        callback_data="skip_health_params"
    ))

    return builder.as_markup()


def verify_profile_keyboard():
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text='✅ Подтвердить', callback_data='confirm_profile'))
    builder.add(InlineKeyboardButton(text='❌ Отменить', callback_data='cancel_profile'))

    return builder.as_markup()
