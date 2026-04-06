from datetime import datetime

from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext

from database import Repository
from states import FriendsHistoryForm
from keyboards import history_friends_keyboard, close_add_fr_keyboard, edit_friend_settings_keyboard
from utils import safe_delete_messages, DateConstants, format_ru_date, WorkoutConstants
from services import get_invite_link

from aiogram.exceptions import TelegramBadRequest

import asyncio

router = Router()


ITEMS_PER_PAGE = 5


def build_friends_caption(history: list, page: int, repo: Repository, user_id: int) -> str:
    total_pages = (len(history) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    start = page * ITEMS_PER_PAGE
    page_items = history[start:start + ITEMS_PER_PAGE]

    caption = '<b>🦎 Список друзей:</b>\n\n'
    if total_pages > 1:
        caption += f'<i>(Страница {page + 1}/{total_pages})</i>\n\n'

    for number, friend in enumerate(page_items, start=start + 1):
        user = repo.users.get_user(friend["receiver_id"])
        username = f'@{user["username"]}' if user else str(friend["receiver_id"])
        notification_status = "🔔" if repo.friends.get_notification_status(user_id, friend["receiver_id"]) else "🔕"
        dt = datetime.strptime(friend['created_at'], "%Y-%m-%d %H:%M:%S")
        date_str = f'{dt.day} {DateConstants.MONTHS.get(dt.month)} {dt.hour:02d}:{dt.minute:02d}'

        caption += (
            f'<b>{number}.</b> {notification_status}👤 {username}\n'
            f'<blockquote><b>Добавлен:</b> {date_str}</blockquote>\n\n'
        )

    return caption


async def send_friends_message(bot, chat_id: int, state: FSMContext, repo: Repository, user_id: int):
    data = await state.get_data()

    history = data['history']
    current_page = data.get('current_page', 0)
    total_pages = (len(history) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    print(len(history))

    caption = build_friends_caption(history, page=current_page, repo=repo, user_id=user_id)
    photo_id = repo.users.paste_decoration_id('friends')

    sent = await bot.send_photo(
        chat_id=chat_id,
        photo=photo_id,
        caption=caption,
        reply_markup=history_friends_keyboard(current_page=current_page, count_friends=len(history), total_pages=total_pages),
        parse_mode='HTML',
    )
    await state.update_data(
        friends_photo_message_id=sent.message_id,
        messages_to_delete=[],
        total_pages=total_pages
    )
    return sent


@router.callback_query(F.data.startswith('accept_friend:'))
async def accept_friend_request(callback: types.CallbackQuery, repo: Repository):
    requester_id = int(callback.data.split(':')[1])
    inviter_id = callback.from_user.id

    repo.friends.add_friend_request(requester_id, inviter_id)

    inviter_name = callback.from_user.username or callback.from_user.full_name
    requester_info = repo.users.get_user(requester_id)

    try:
        await callback.bot.send_message(chat_id=requester_id,
                                        text=f'🎉 <b>@{inviter_name}</b> принял твой запрос в друзья!\n\n',
                                        parse_mode='HTML')
    except Exception:
        pass

    requester_name = requester_info.get('username', str(requester_id)) if requester_info else str(requester_id)
    msg = await callback.message.edit_text(
        f'✅ <b>Вы теперь друзья с @{requester_name}!</b>',
        parse_mode='HTML',
    )
    await asyncio.sleep(7)
    await msg.delete()

    await callback.answer()


@router.callback_query(F.data.startswith('decline_friend:'))
async def decline_friend_request(callback: types.CallbackQuery, repo: Repository):
    requester_id = int(callback.data.split(':')[1])
    # inviter_id = callback.from_user.id

    requester_info = repo.users.get_user(requester_id)
    requester_name = requester_info.get('username', str(requester_id)) if requester_info else str(requester_id)

    msg = await callback.message.edit_text(
        f'🙅‍♂️ <b>Запрос дружбы был отклонен с @{requester_name}!</b>',
        parse_mode='HTML',
    )
    await asyncio.sleep(7)
    await msg.delete()

    await callback.answer()





@router.callback_query(FriendsHistoryForm.viewing, F.data == 'close_friends')
async def close_add_friend_handler(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    await safe_delete_messages(callback.bot, callback.message.chat.id, [data.get('friends_photo_message_id', [])])

    await callback.answer()


@router.callback_query(FriendsHistoryForm.viewing, F.data == 'close_add_friend')
async def close_friends_handler(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    await safe_delete_messages(callback.bot, callback.message.chat.id, [data.get('add_friend_message_id', [])])

    await callback.answer()






@router.callback_query(F.data == 'friends')
async def show_friends(callback: types.CallbackQuery, state: FSMContext, repo: Repository):
    history = repo.friends.get_friends_list(callback.from_user.id)

    if not history:
        photo_id = repo.users.paste_decoration_id('friends')
        caption = (
            f'<b>🦎 Список друзей:</b>\n\n'
            f'<blockquote>Список друзей на данный момент пуст</blockquote>\n\n'
            f'Ты можешь использовать функцию: <b>"➕ Добавить друга"</b>, чтобы здесь появились твои первые друзья!'
        )
        sent = await callback.message.answer_photo(
            photo=photo_id, caption=caption,
            reply_markup=history_friends_keyboard(), parse_mode='HTML'
        )
        await state.update_data(friends_photo_message_id=sent.message_id)
        await state.set_state(FriendsHistoryForm.viewing)
        await callback.answer()
        return

    await state.update_data(history=history, current_page=0)
    await send_friends_message(callback.bot, callback.message.chat.id, state, repo, callback.from_user.id)
    await state.set_state(FriendsHistoryForm.viewing)

    await callback.answer()


@router.callback_query(FriendsHistoryForm.viewing, F.data.startswith('page_friends:'))
async def handle_friends_page(callback: types.CallbackQuery, state: FSMContext, repo: Repository):
    action = callback.data.split(':')[1]
    data = await state.get_data()

    history = data['history']
    page = data['current_page']
    total_pages = (len(history) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    if action == 'next' and page < total_pages - 1:
        page += 1
    elif action == 'prev' and page > 0:
        page -= 1
    else:
        await callback.answer()
        return

    await state.update_data(current_page=page)
    caption = build_friends_caption(history, page=page, repo=repo, user_id=callback.from_user.id)

    sent = await callback.message.edit_caption(
        caption=caption,
        reply_markup=history_friends_keyboard(current_page=page, count_friends=len(history), total_pages=total_pages),
        parse_mode='HTML',
    )
    await state.update_data(messages_to_delete=[sent.message_id])
    await callback.answer()


@router.callback_query(FriendsHistoryForm.viewing, F.data == 'select_page_friends')
async def select_friends_page(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    total_pages = (len(data['history']) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    await state.set_state(FriendsHistoryForm.selecting_page)
    sent = await callback.message.answer(
        f'⚡️<b>Введи номер страницы от 1 до {total_pages}:</b>',
        parse_mode='HTML'
    )
    await state.update_data(messages_to_delete=[sent.message_id])
    await callback.answer()


@router.message(FriendsHistoryForm.selecting_page)
async def jump_to_friends_page(message: types.Message, state: FSMContext, repo: Repository):
    data = await state.get_data()
    total_pages = (len(data['history']) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    await message.delete()
    await safe_delete_messages(message.bot, message.chat.id, data.get('messages_to_delete', []))

    if not message.text.isdigit() or not (1 <= int(message.text) <= total_pages):
        await message.answer(f'❌ Введи корректное число от 1 до {total_pages}')
        return

    new_page = int(message.text) - 1
    await state.update_data(current_page=new_page)
    await state.set_state(FriendsHistoryForm.viewing)

    caption = build_friends_caption(data['history'], page=new_page, repo=repo, user_id=message.from_user.id)

    friends_photo_id = data.get('friends_photo_message_id')
    if friends_photo_id:
        sent = await message.bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=friends_photo_id,
            caption=caption,
            reply_markup=history_friends_keyboard(current_page=new_page, count_friends=len(data['history']), total_pages=total_pages),
            parse_mode='HTML',
        )
    else:
        sent = await send_friends_message(message.bot, message.chat.id, state, repo, message.from_user.id)

    await state.update_data(messages_to_delete=[sent.message_id])


@router.callback_query(FriendsHistoryForm.viewing, F.data == 'add_friend')
async def handle_add_friend(callback: types.CallbackQuery, state: FSMContext):
    friend_link = await get_invite_link(callback.bot, callback.from_user.id)

    text = (
        f'<b>🦎 Добавление друзей:</b>\n\n'
        f'<blockquote>Отправь эту ссылку будущему другу. Когда он перейдёт по ней, ты получишь <b>уведомление</b> и сможешь подтвердить добавление в друзья!</blockquote>\n\n'
        f'🔗 <b>Твоя ссылка для дружбы:</b>\n'
        f'<code>{friend_link}</code>\n\n'
        f'<i>(Нажми на ссылку, чтобы скопировать)</i>'
    )
    sent = await callback.message.answer(
        text=text,
        reply_markup=close_add_fr_keyboard(),
        parse_mode='HTML'
    )
    await state.update_data(add_friend_message_id=sent.message_id)
    await callback.answer()







@router.callback_query(FriendsHistoryForm.viewing, F.data == 'choose_friend')
async def choose_friend(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    page = data['current_page']
    start_idx = page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE

    history = data['history']
    if end_idx >= len(history):
        end_idx = len(history)

    sent = await callback.message.answer(
        f"🫵 <b>Выбери номер друга из списка выше ({start_idx + 1}-{end_idx}):</b>",
        parse_mode='HTML'
    )

    await state.update_data(messages_to_delete=[sent.message_id])
    await state.set_state(FriendsHistoryForm.viewing_friend)
    await callback.answer()


@router.message(FriendsHistoryForm.viewing_friend)
async def handle_friend_selection(message: types.Message, state: FSMContext, repo: Repository):
    data = await state.get_data()

    await message.delete()
    await safe_delete_messages(message.bot, message.chat.id, data.get('messages_to_delete', []))

    if not message.text.isdigit():
        await message.answer("Пожалуйста, отправьте порядковый номер друга цифрой.")
        return

    friend_number = int(message.text)
    history = data['history']
    page = data['current_page']
    start_idx = page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE

    if not (start_idx < friend_number <= min(end_idx, len(history))):
        await message.answer('❌ Введи корректный номер друга из списка выше')
        return

    selected_friend = history[friend_number - 1]
    friend_id = selected_friend['receiver_id']

    await state.update_data(user_id=message.from_user.id, friend_id=friend_id)

    friend_info = repo.users.get_user(friend_id)
    friend_username = friend_info.get('username', str(friend_id)) if friend_info else str(friend_id)

    friend_goal_data = repo.goals.get_latest_goal(friend_id)

    if not friend_goal_data:
        await message.answer("У этого друга пока нет активной цели.")
        return

    goal_created_at = format_ru_date(friend_goal_data["created_at"])
    goal_deadline = format_ru_date(friend_goal_data["deadline"])

    user_gender = repo.profiles.get_user_profile(friend_id)['gender']
    photo_id = repo.users.paste_decoration_id(f'friend_{user_gender}')

    history_workouts = repo.workouts.get_history(friend_id, 7)

    if history_workouts:
        quantity_workouts = len(history_workouts)
        avg_intensivity = round(
            sum(int(row['intensity']) for row in history_workouts) / quantity_workouts,
            1
        )

        avg_workouts_duration = round(
            sum(int(row['duration']) for row in history_workouts) / quantity_workouts,
            1
        )

        caption = ( 
                f'<b>🔽 Статистика За 7 Дней</b>\n'
                f'<blockquote><b>Кол-во тренировок:</b> 🏌️‍♀️{quantity_workouts}</blockquote>\n\n'
                f'<blockquote><b>📊Средние значения:</b>\n<b>Интенсивность:</b> ⚡️{avg_intensivity}/{WorkoutConstants.MAX_INTENSITY}\n<b>Длительность:</b> ⏳{avg_workouts_duration} (мин.)</blockquote>'
        )
    else:
        caption = (
            f'<b>🔽 Статистика За 7 Дней:</b>\n'
            f'<blockquote>❌ За последние 7 дней тренировок нет</blockquote>'
        )

    is_notifications_on = bool(repo.friends.get_notification_status(message.from_user.id, friend_id))
    notification_status = "🔔 ВКЛ" if is_notifications_on else "🔕 ВЫКЛ"
    text = (
        f'👤 <b>Информация о друге:</b>\n\n'
        f'<b>Уведомления о тренировках:</b>\n{notification_status}\n\n'
        f'🔹 <b>Имя:</b> @{friend_username}\n\n'
        f'<blockquote>'
        f'🎯 <b>Цель:</b> {friend_goal_data["goal"]}\n\n'
        f'<b>Добавлена:</b> {goal_created_at}\n'
        f'<b>⏰ Дедлайн:</b> {goal_deadline}'
        f'</blockquote>\n\n'
        f'{caption}'
    )

    sent = await message.answer_photo(photo=photo_id, caption=text,
                                        reply_markup=edit_friend_settings_keyboard(is_notifications_on), parse_mode='HTML')
    
    await state.update_data(messages_to_delete=[sent.message_id], user_id=message.from_user.id, friend_id=friend_id)


@router.callback_query(FriendsHistoryForm.viewing_friend, F.data == "delete_friend")
async def delete_friend(callback: types.CallbackQuery, state: FSMContext, repo: Repository):
    data = await state.get_data()

    await safe_delete_messages(callback.bot, callback.message.chat.id, data.get('messages_to_delete', []))
    repo.friends.delete_friendship(data['user_id'], data['friend_id'])

    updated_history = repo.friends.get_friends_list(data['user_id'])
    current_page = data.get('current_page', 0)
    total_pages = max((len(updated_history) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE, 1)

    if current_page >= total_pages:
        current_page = max(total_pages - 1, 0)

    await state.update_data(history=updated_history, current_page=current_page)

    friends_photo_message_id = data.get('friends_photo_message_id')

    if not updated_history:
        photo_id = repo.users.paste_decoration_id('friends')
        caption = (
            f'<b>🦎 Список друзей:</b>\n\n'
            f'<blockquote>Список друзей на данный момент пуст</blockquote>\n\n'
            f'Ты можешь использовать функцию: <b>"➕ Добавить друга"</b>, чтобы здесь появились твои первые друзья!'
        )
        if friends_photo_message_id:
            await callback.bot.edit_message_caption(
                chat_id=callback.message.chat.id,
                message_id=friends_photo_message_id,
                caption=caption,
                reply_markup=history_friends_keyboard(),
                parse_mode='HTML',
            )
        else:
            sent = await callback.message.answer_photo(
                photo=photo_id, caption=caption,
                reply_markup=history_friends_keyboard(), parse_mode='HTML'
            )
            await state.update_data(messages_to_delete=[sent.message_id])
    else:
        caption = build_friends_caption(updated_history, page=current_page, repo=repo, user_id=data['user_id'])
        if friends_photo_message_id:
            await callback.bot.edit_message_caption(
                chat_id=callback.message.chat.id,
                message_id=friends_photo_message_id,
                caption=caption,
                reply_markup=history_friends_keyboard(
                    current_page=current_page,
                    count_friends=len(updated_history),
                    total_pages=total_pages,
                ),
                parse_mode='HTML',
            )
        else:
            await send_friends_message(callback.bot, callback.message.chat.id, state, repo, data['user_id'])

    await state.set_state(FriendsHistoryForm.viewing)
    await callback.answer('✅ Друг был удалён', show_alert=True)


@router.callback_query(FriendsHistoryForm.viewing_friend, F.data == 'close_friend_settings')
async def close_friend_settings(callback: types.CallbackQuery, state: FSMContext, repo: Repository):
    data = await state.get_data()

    await safe_delete_messages(callback.bot, callback.message.chat.id, data.get('messages_to_delete', []))

    friends_photo_message_id = data.get('friends_photo_message_id')
    current_page = data.get('current_page')
    history = data.get('history')
    total_pages = data.get('total_pages')

    try:
        await callback.bot.edit_message_caption(
            chat_id=callback.message.chat.id,
            message_id=friends_photo_message_id,
            caption=build_friends_caption(history, page=current_page, repo=repo, user_id=callback.from_user.id),
            reply_markup=history_friends_keyboard(current_page=current_page,
                                                count_friends=len(history),
                                                    total_pages=total_pages),
            parse_mode='HTML',
        )
    except TelegramBadRequest as e:
        if 'message is not modified' not in str(e):
            raise 


    await state.set_state(FriendsHistoryForm.viewing)
    await callback.answer()


@router.callback_query(FriendsHistoryForm.viewing_friend, F.data.startswith('friend_notifications_'))
async def toggle_friend_notifications(callback: types.CallbackQuery, state: FSMContext, repo: Repository):
    data = await state.get_data()
    
    friend_id = data['friend_id']
    user_id = data['user_id']

    new_status = 1 if callback.data.endswith('_1') else 0
    repo.friends.set_notification_status(user_id, friend_id, new_status)

    is_notifications_on = bool(repo.friends.get_notification_status(user_id, friend_id))

    friends_photo_message_id = data.get('friends_photo_message_id')
    current_page = data.get('current_page')
    history = data.get('history')
    total_pages = data.get('total_pages')

    try:
        await callback.bot.edit_message_caption(
            chat_id=callback.message.chat.id,
            message_id=friends_photo_message_id,
            caption=build_friends_caption(history, page=current_page, repo=repo, user_id=user_id),
            reply_markup=history_friends_keyboard(current_page=current_page,
                                                count_friends=len(history),
                                                    total_pages=total_pages),
            parse_mode='HTML',
        )
    except TelegramBadRequest as e:
        if 'message is not modified' not in str(e):
            raise 

    await callback.answer(f'Уведомления для этого друга {"включены" if is_notifications_on else "выключены"}', show_alert=True)







# @router.message(WorkoutHistoryForm.history)
# async def handle_history_input(message: types.Message, state: FSMContext, repo: Repository):
#     data = await state.get_data()

#     await message.delete()
#     await safe_delete_messages(message.bot, message.chat.id, data['messages_to_delete'])

#     if not message.text.isdigit():
#         await message.answer('Введи натуральное число:')
#         return