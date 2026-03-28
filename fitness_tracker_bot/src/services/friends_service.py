from aiogram.utils.deep_linking import create_start_link
from aiogram import Bot, types

from middlewares import Repository
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def get_invite_link(bot: Bot, user_id: int) -> str:
    payload = f"add_{user_id}"
    return await create_start_link(bot, payload, encode=True)


async def handle_friend_invite(message: types.Message, inviter_id: int, repo: Repository):
    bot: Bot = message.bot
    invited_id = message.from_user.id
    invited_name = message.from_user.full_name

    # 1. Защита от само-добавления
    if inviter_id == invited_id:
        await message.answer("💡 Вы не можете добавить в друзья самого себя.")
        return

    # 2. Проверка, не друзья ли они уже (метод в repo нужно создать)
    if repo.friends.are_already_friends(inviter_id, invited_id):
        await message.answer("👥 Вы уже являетесь друзьями с этим пользователем!")
        return

    # 3. Отправляем уведомление тому, КТО пригласил (Inviter)
    try:
        builder = InlineKeyboardBuilder()
        # В callback_data передаем ID того, кто постучался в друзья
        builder.button(text="✅ Подтвердить", callback_data=f"accept_friend:{invited_id}")
        builder.button(text="❌ Отклонить", callback_data=f"decline_friend:{invited_id}")
        builder.adjust(2)

        await bot.send_message(
            chat_id=inviter_id,
            text=(
                f"🔔 <b>Новая заявка в друзья!</b>\n\n"
                f"Пользователь <a href='tg://user?id={invited_id}'>{invited_name}</a> "
                f"хочет добавить вас в друзья. Подтверждаете?"
            ),
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
        
        # 4. Сообщаем тому, КТО перешел по ссылке (Invited)
        await message.answer(
            "✉️ <b>Запрос отправлен!</b>\n"
            "Мы уведомили пользователя. Как только он нажмет «Подтвердить», "
            "вы получите уведомление."
        )

    except Exception as e:
        # Если пригласивший заблокировал бота или что-то пошло не так
        await message.answer("⚠️ Не удалось отправить запрос. Возможно, пользователь заблокировал бота.")