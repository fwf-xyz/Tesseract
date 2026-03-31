# from datetime import datetime

from aiogram import types, F, Router
# from aiogram.fsm.context import FSMContext

# from database import Repository
# from states import FriendsHistoryForm
# from keyboards import history_friends_keyboard, close_add_fr_keyboard, friend_request_keyboard
# from utils import safe_delete_messages
# from services import get_invite_link

router = Router()


# ITEMS_PER_PAGE = 10


# def build_friends_caption(history: list, page: int) -> str:
#     total_pages = (len(history) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
#     start = page * ITEMS_PER_PAGE
#     page_items = history[start:start + ITEMS_PER_PAGE]

#     caption = '<b>🦎 Список друзей:</b>\n'
#     caption += '\n<i>(Страница {}/{})</i>\n\n ------------ \n'.format(page + 1, total_pages)

#     for number, friend in enumerate(page_items, start=start + 1):
#         dt = datetime.strptime(friend['joined_at'], "%Y-%m-%d %H:%M:%S")
#         date_str = "{:02d}.{:02d}.{} {:02d}:{:02d}".format(
#             dt.day, dt.month, dt.year, dt.hour, dt.minute
#         )
#         caption += '<b>{}.</b> <blockquote>👤 {}</blockquote>\n\n<b>Присоединился:</b> {}\n\n'.format(
#             number,
#             friend.get('username'),
#             date_str,
#         )
#     caption += '------------\n'
#     return caption


# async def send_friends_message(bot, chat_id: int, state: FSMContext, repo: Repository):
#     data = await state.get_data()
#     history = data['history']
#     current_page = data.get('current_page', 0)
#     total_pages = (len(history) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

#     caption = build_friends_caption(history, page=current_page)
#     photo_id = repo.users.paste_decoration_id('friends')

#     sent = await bot.send_photo(
#         chat_id=chat_id,
#         photo=photo_id,
#         caption=caption,
#         reply_markup=history_friends_keyboard(current_page=current_page, total_pages=total_pages),
#         parse_mode='HTML',
#     )
#     await state.update_data(
#         messages_to_delete=[sent.message_id],
#         friends_photo_message_id=sent.message_id,
#     )
#     return sent


# # ─────────────────────────────────────────────
# #  Deep-link: /start friend_<inviter_id>
# #  Срабатывает когда новый пользователь
# #  переходит по реферальной ссылке друга
# # ─────────────────────────────────────────────

# @router.message(F.text.regexp(r'^/start friend_(\d+)$'))
# async def handle_friend_deeplink(message: types.Message, repo: Repository):
#     inviter_id = int(message.text.split('friend_')[1])
#     requester = message.from_user

#     if requester.id == inviter_id:
#         await message.answer('❌ Нельзя добавить самого себя в друзья.')
#         return

#     # Проверяем, не друзья ли уже
#     if repo.friends.are_friends(inviter_id, requester.id):
#         await message.answer('ℹ️ Вы уже являетесь друзьями!')
#         return

#     # Проверяем, нет ли уже активного запроса
#     if repo.friends.request_exists(inviter_id, requester.id):
#         await message.answer('⏳ Запрос в друзья уже отправлен. Ожидай подтверждения!')
#         return

#     # Сохраняем запрос в БД
#     repo.friends.create_friend_request(
#         from_user_id=requester.id,
#         to_user_id=inviter_id,
#     )

#     requester_name = requester.username

#     # Уведомляем инвайтера
#     try:
#         await message.bot.send_message(
#             chat_id=inviter_id,
#             text=(
#                 f'<b>🦎 Запрос в друзья!</b>\n\n'
#                 f'Пользователь <b>@{requester_name}</b> хочет добавить тебя в друзья.\n\n'
#                 f'Принять запрос?'
#             ),
#             reply_markup=friend_request_keyboard(requester_id=requester.id),
#             parse_mode='HTML',
#         )
#     except Exception:
#         # Инвайтер мог заблокировать бота — молча пропускаем
#         pass

#     await message.answer(
#         f'✅ Запрос в друзья отправлен!\n\n'
#         f'Как только он подтвердит — ты получишь уведомление.'
#     )


# # ─────────────────────────────────────────────
# #  Принятие запроса в друзья
# # ─────────────────────────────────────────────

# @router.callback_query(F.data.startswith('accept_friend:'))
# async def accept_friend_request(callback: types.CallbackQuery, repo: Repository):
#     requester_id = int(callback.data.split(':')[1])
#     inviter_id = callback.from_user.id

#     # Повторная проверка — вдруг запрос уже обработан
#     if not repo.friends.request_exists(requester_id, inviter_id):
#         await callback.message.edit_text('ℹ️ Этот запрос уже был обработан.')
#         await callback.answer()
#         return

#     repo.friends.accept_friend_request(
#         from_user_id=requester_id,
#         to_user_id=inviter_id,
#     )

#     inviter_name = callback.from_user.username or callback.from_user.full_name

#     # Редактируем сообщение у инвайтера
#     requester_info = repo.users.get_user(requester_id)
#     requester_name = requester_info.get('username', str(requester_id)) if requester_info else str(requester_id)

#     await callback.message.edit_text(
#         f'✅ <b>Вы теперь друзья с @{requester_name}!</b>',
#         parse_mode='HTML',
#     )

#     # Уведомляем того, кто отправлял запрос
#     try:
#         await callback.bot.send_message(
#             chat_id=requester_id,
#             text=(
#                 f'🎉 <b>@{inviter_name}</b> принял твой запрос в друзья!\n\n'
#                 f'Теперь вы друзья 🦎'
#             ),
#             parse_mode='HTML',
#         )
#     except Exception:
#         pass

#     await callback.answer('✅ Запрос принят!')


# # ─────────────────────────────────────────────
# #  Отклонение запроса в друзья
# # ─────────────────────────────────────────────

# @router.callback_query(F.data.startswith('decline_friend:'))
# async def decline_friend_request(callback: types.CallbackQuery, repo: Repository):
#     requester_id = int(callback.data.split(':')[1])
#     inviter_id = callback.from_user.id

#     if not repo.friends.request_exists(requester_id, inviter_id):
#         await callback.message.edit_text('ℹ️ Этот запрос уже был обработан.')
#         await callback.answer()
#         return

#     repo.friends.decline_friend_request(
#         from_user_id=requester_id,
#         to_user_id=inviter_id,
#     )


# # ─────────────────────────────────────────────
# #  Закрытие меню "Добавить друга"
# # ─────────────────────────────────────────────

# @router.callback_query(FriendsHistoryForm.viewing, F.data == 'close_add_friend')
# async def close_add_friend_handler(callback: types.CallbackQuery, state: FSMContext):
#     data = await state.get_data()

#     await safe_delete_messages(callback.bot, callback.message.chat.id, data.get('messages_to_delete', []))
#     await safe_delete_messages(callback.bot, callback.message.chat.id, data.get('add_friend_message_id', []))

#     await callback.answer()


# @router.callback_query(FriendsHistoryForm.viewing, F.data == 'close_friends')
# async def close_friends_handler(callback: types.CallbackQuery, state: FSMContext):
#     data = await state.get_data()

#     await safe_delete_messages(callback.bot, callback.message.chat.id, data.get('messages_to_delete', []))

#     await state.clear()
#     await callback.answer()


# @router.callback_query(F.data == 'friends')
# async def show_friends(callback: types.CallbackQuery, state: FSMContext, repo: Repository):
#     history = repo.friends.get_friends_list(callback.from_user.id)

#     if not history:
#         photo_id = repo.users.paste_decoration_id('friends')
#         caption = (
#             f'<b>🦎 Список друзей:</b>\n\n'
#             f'<blockquote>Список друзей на данный момент пуст</blockquote>\n\n'
#             f'Ты можешь использовать функцию: <b>"➕ Добавить друга"</b>, чтобы здесь появились твои первые друзья!'
#         )
#         sent = await callback.message.answer_photo(
#             photo=photo_id, caption=caption,
#             reply_markup=history_friends_keyboard(), parse_mode='HTML'
#         )
#         await state.update_data(messages_to_delete=[sent.message_id])
#         await state.set_state(FriendsHistoryForm.viewing)
#         await callback.answer()
#         return

#     await state.update_data(history=history, current_page=0)
#     await send_friends_message(callback.bot, callback.message.chat.id, state, repo)
#     await state.set_state(FriendsHistoryForm.viewing)
#     await callback.answer()


# @router.callback_query(FriendsHistoryForm.viewing, F.data.startswith('page_friends:'))
# async def handle_friends_page(callback: types.CallbackQuery, state: FSMContext):
#     action = callback.data.split(':')[1]
#     data = await state.get_data()

#     history = data['history']
#     page = data['current_page']
#     total_pages = (len(history) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

#     if action == 'next' and page < total_pages - 1:
#         page += 1
#     elif action == 'prev' and page > 0:
#         page -= 1
#     else:
#         await callback.answer()
#         return

#     await state.update_data(current_page=page)
#     caption = build_friends_caption(history, page=page)

#     sent = await callback.message.edit_caption(
#         caption=caption,
#         reply_markup=history_friends_keyboard(current_page=page, total_pages=total_pages),
#         parse_mode='HTML',
#     )
#     await state.update_data(messages_to_delete=[sent.message_id])
#     await callback.answer()


# @router.callback_query(FriendsHistoryForm.viewing, F.data == 'select_page_friends')
# async def select_friends_page(callback: types.CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     total_pages = (len(data['history']) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

#     await state.set_state(FriendsHistoryForm.selecting_page)
#     sent = await callback.message.answer(
#         f'⚡️<b>Введи номер страницы от 1 до {total_pages}:</b>',
#         parse_mode='HTML'
#     )
#     await state.update_data(messages_to_delete=[sent.message_id])
#     await callback.answer()


# @router.message(FriendsHistoryForm.selecting_page)
# async def jump_to_friends_page(message: types.Message, state: FSMContext, repo: Repository):
#     data = await state.get_data()
#     total_pages = (len(data['history']) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

#     await message.delete()
#     await safe_delete_messages(message.bot, message.chat.id, data.get('messages_to_delete', []))

#     if not message.text.isdigit() or not (1 <= int(message.text) <= total_pages):
#         await message.answer(f'❌ Введи корректное число от 1 до {total_pages}')
#         return

#     new_page = int(message.text) - 1
#     await state.update_data(current_page=new_page)
#     await state.set_state(FriendsHistoryForm.viewing)

#     caption = build_friends_caption(data['history'], page=new_page)

#     friends_photo_id = data.get('friends_photo_message_id')
#     if friends_photo_id:
#         sent = await message.bot.edit_message_caption(
#             chat_id=message.chat.id,
#             message_id=friends_photo_id,
#             caption=caption,
#             reply_markup=history_friends_keyboard(current_page=new_page, total_pages=total_pages),
#             parse_mode='HTML',
#         )
#     else:
#         sent = await send_friends_message(message.bot, message.chat.id, state, repo)

#     await state.update_data(messages_to_delete=[sent.message_id])


# @router.callback_query(FriendsHistoryForm.viewing, F.data == 'add_friend')
# async def handle_add_friend(callback: types.CallbackQuery, state: FSMContext):
#     friend_link = await get_invite_link(callback.bot, callback.from_user.id)

#     text = (
#         f'<b>🦎 Добавление друзей:</b>\n\n'
#         f'<blockquote>Отправь эту ссылку будущему другу. Когда он перейдёт по ней, ты получишь <b>уведомление</b> и сможешь подтвердить добавление в друзья!</blockquote>\n\n'
#         f'🔗 <b>Твоя ссылка для дружбы:</b>\n'
#         f'<code>{friend_link}</code>\n\n'
#         f'<i>(Нажми на ссылку, чтобы скопировать)</i>'
#     )
#     sent = await callback.message.answer(
#         text=text,
#         reply_markup=close_add_fr_keyboard(),
#         parse_mode='HTML'
#     )
#     await state.update_data(add_friend_message_id=sent.message_id)
#     await callback.answer()