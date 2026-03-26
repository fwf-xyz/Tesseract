from aiogram.utils.deep_linking import create_start_link
from aiogram import Bot

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from middlewares import Repository


async def get_invite_link(bot: Bot, user_id: int) -> str:
    payload = f"add_{user_id}"
    return await create_start_link(bot, payload, encode=True)


async def handle_friend_invite(message: types.Message, inviter_id: int, repo: Repository):
    new_user_id = message.from_user.id

    if new_user_id == inviter_id:
        await message.answer("Нельзя добавить самого себя.")
        return

    status = repo.friends.get_status(inviter_id, new_user_id)

    if status == "completed":
        await message.answer("Вы уже друзья!")
        return
    if status == "pending":
        await message.answer("Заявка уже отправлена, ожидайте подтверждения.")
        return
    if status == "rejected":
        await message.answer("Ваша заявка была отклонена ранее.")
        return

    inviter = repo.users.get_user(inviter_id)
    if not inviter:
        await message.answer("Пользователь, который вас пригласил, не найден.")
        return

    repo.friends.create_request(inviter_id, new_user_id)

    await message.answer(
        f"Пользователь <b>{inviter['username']}</b> хочет добавить вас в друзья!",
        parse_mode="HTML"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="✅ Принять",
            callback_data=f"friend_accept_{new_user_id}"
        ),
        InlineKeyboardButton(
            text="❌ Отклонить",
            callback_data=f"friend_reject_{new_user_id}"
        )
    ]])

    await message.bot.send_message(
        chat_id=inviter_id,
        text=f"Пользователь <b>{message.from_user.username}</b> перешёл по твоей ссылке!\n\nДобавить в друзья?",
        parse_mode="HTML",
        reply_markup=kb
    )