from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


def history_friends_keyboard(
            current_page: int = 0, 
            count_friends: int = 0,
            total_pages: int = 1
) -> InlineKeyboardMarkup:
    
    builder = InlineKeyboardBuilder()
    nav_count = 0
    
    if current_page > 0:
        builder.button(text='◀ Назад', callback_data='page_friends:prev')
        nav_count += 1
        
    if current_page < total_pages - 1:
        builder.button(text='Вперёд ▶', callback_data='page_friends:next')
        nav_count += 1
        
    if total_pages > 1:
        builder.button(text='⚡️ Быстрый выбор страницы', callback_data='select_page_friends')
        
    if count_friends > 0:
        builder.button(text='🫵 Выбрать друга', callback_data='choose_friend')

    builder.button(text='➕ Добавить друга', callback_data='add_friend')
    
    builder.button(text='× Закрыть', callback_data='close_friends')
    
    if nav_count:
        builder.adjust(nav_count, 1)
    else:
        builder.adjust(1)
        
    return builder.as_markup()


def close_add_fr_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text='× Закрыть', callback_data='close_add_friend')

    return builder.as_markup()


def verify_request_friend(invited_id):
    builder = InlineKeyboardBuilder()

    builder.button(text="✅ Подтвердить", callback_data=f"accept_friend:{invited_id}")
    builder.button(text="❌ Отклонить", callback_data=f"decline_friend:{invited_id}")

    builder.adjust(2)

    return builder.as_markup()


def edit_friend_settings_keyboard(notofication_status: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if notofication_status:
        builder.button(text="🔕 ВЫКЛ уведомления", callback_data="friend_notifications_0")
    else:
        builder.button(text="🔔 ВКЛ уведомления", callback_data="friend_notifications_1")
        
    builder.button(text="❌ Удалить из друзей", callback_data="delete_friend")
    builder.button(text='× Закрыть', callback_data='close_friend_settings')

    builder.adjust(1, 1, 1)

    return builder.as_markup()