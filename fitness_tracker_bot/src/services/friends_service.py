from aiogram.utils.deep_linking import create_start_link
from aiogram import Bot, types

from middlewares import Repository

from keyboards import verify_request_friend

import asyncio


async def get_invite_link(bot: Bot, user_id: int) -> str:
    payload = f"add_{user_id}"
    return await create_start_link(bot, payload, encode=True)


async def handle_friend_invite(message: types.Message, inviter_id: int, repo: Repository):
    bot: Bot = message.bot
    invited_id = message.from_user.id
    invited_name = message.from_user.full_name

    if inviter_id == invited_id:
        msg = await message.answer("❌ <b>Нельзя добавить в друзья самого себя!</b>", parse_mode='HTML')
        await asyncio.sleep(5)
        await msg.delete()
        return
    
    if repo.friends.get_relationship_status(inviter_id, invited_id):
        msg =await message.answer("👥 <b>Вы уже являетесь друзьями с этим пользователем!</b>", parse_mode='HTML')
        await asyncio.sleep(5)
        await msg.delete()
        return

    try:
        await bot.send_message(
            chat_id=inviter_id,
            text=(
                f"<b>🦎 Запрос в друзья!</b>\n\n"
                f"<blockquote>Пользователь <i><a href='tg://user?id={invited_id}'>{invited_name}</a></i> хочет добавить тебя в друзья</blockquote>\n\n"
                f'<b>Подтвердить заявку?</b>'
            ),
            reply_markup=verify_request_friend(invited_id),
            parse_mode="HTML"
        )
        
        await message.answer(
            "📩 <b>Заявка в друзья отправлена!</b>\n\n"
            "<blockquote>Как только пользователь нажмет кнопку: «✅ Подтвердить», ты получишь оповещение</blockquote>",
            parse_mode="HTML"
        )

    except Exception as e:
        await message.answer("⚠️ <b>Не удалось отправить запрос. Возможно, пользователь заблокировал бота</b>", parse_mode='HTML')