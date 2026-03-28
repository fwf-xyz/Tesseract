from datetime import datetime

from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext

from database import Repository
from states import FriendsHistoryForm 
from keyboards import history_friends_keyboard, close_add_fr_keyboard
from utils import safe_delete_messages
from services import get_invite_link

router = Router()


ITEMS_PER_PAGE = 3


def build_friends_caption(history: list, page: int) -> str:
    total_pages = (len(history) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    start = page * ITEMS_PER_PAGE
    page_items = history[start:start + ITEMS_PER_PAGE]

    caption = '<b>🦎 Список друзей:</b>\n'

    caption += '\n<i>(Страница {}/{})</i>\n\n ------------ \n'.format(page + 1, total_pages)

    for number, friend in enumerate(page_items, start=start + 1):
        dt = datetime.strptime(friend['joined_at'], "%Y-%m-%d %H:%M:%S")
        date_str = "{:02d}.{:02d}.{} {:02d}:{:02d}".format(
            dt.day, dt.month, dt.year, dt.hour, dt.minute
        )
        caption += '<b>{}.</b> <blockquote>👤 {}</blockquote>\n\n<b>Присоединился:</b> {}\n\n'.format(
            number,
            friend.get('username'),
            date_str,
        )
    caption += '------------\n'
    return caption


async def send_friends_message(bot, chat_id: int,
                            state: FSMContext, repo: Repository):
    data = await state.get_data()
    history = data['history']
    current_page = data.get('current_page', 0)
    total_pages = (len(history) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    caption = build_friends_caption(history, page=current_page)

    photo_id = repo.users.paste_decoration_id('friends')

    sent = await bot.send_photo(
        chat_id=chat_id,
        photo=photo_id,
        caption=caption,
        reply_markup=history_friends_keyboard(current_page=current_page, total_pages=total_pages),
        parse_mode='HTML',
    )
    await state.update_data(
        messages_to_delete=[sent.message_id],
        friends_photo_message_id=sent.message_id,
    )
    return sent


@router.callback_query(FriendsHistoryForm.viewing, F.data == 'close_friends')
async def close_friends_handler(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await safe_delete_messages(callback.bot, callback.message.chat.id, data.get('messages_to_delete', []))

    await state.clear()
    await callback.answer()





@router.callback_query(F.data == 'friends')
async def show_friends(callback: types.CallbackQuery,
                        state: FSMContext, repo: Repository):
    history = repo.friends.get_friends_list(callback.from_user.id)

    if not history:
        photo_id = repo.users.paste_decoration_id('friends')
        caption=(
                f'<b>🦎 Список друзей:</b>\n\n'
                f'<blockquote>Список друзей на данный момент пуст</blockquote>\n\n'
                f'Ты можешь использовать функцию: <b>"➕ Добавить друга"</b>, чтобы здесь появились твои первые друзья!'
        )
        sent = await callback.message.answer_photo(photo=photo_id, caption=caption, reply_markup=history_friends_keyboard(), parse_mode='HTML')

        await state.update_data(messages_to_delete=[sent.message_id])
        await state.set_state(FriendsHistoryForm.viewing)
        await callback.answer()
        return

    await state.update_data(history=history, current_page=0)
    await send_friends_message(callback.bot, callback.message.chat.id, state, repo)
    await state.set_state(FriendsHistoryForm.viewing)
    await callback.answer()


@router.callback_query(FriendsHistoryForm.viewing, F.data.startswith('page_friends:'))
async def handle_friends_page(callback: types.CallbackQuery, state: FSMContext):
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

    caption = build_friends_caption(history, page=page)

    sent = await callback.message.edit_caption(
        caption=caption,
        reply_markup=history_friends_keyboard(current_page=page, total_pages=total_pages),
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
        await message.answer(f"❌ Введи корректное число от 1 до {total_pages}")
        return

    new_page = int(message.text) - 1
    await state.update_data(current_page=new_page)
    await state.set_state(FriendsHistoryForm.viewing)

    caption = build_friends_caption(data['history'], page=new_page)

    friends_photo_id = data.get('friends_photo_message_id')
    if friends_photo_id:
        sent = await message.bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=friends_photo_id,
            caption=caption,
            reply_markup=history_friends_keyboard(current_page=new_page, total_pages=total_pages),
            parse_mode='HTML',
        )
    else:
        sent = await send_friends_message(message.bot, message.chat.id, state, repo)

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
    sent = await callback.message.answer(text=text,
                                        reply_markup= close_add_fr_keyboard(),
                                        parse_mode='HTML')

    await state.update_data(messages_to_delete=[sent.message_id])
    await callback.answer()


# @router.callback_query()

