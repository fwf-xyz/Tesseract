import logging

async def safe_delete_messages(bot, chat_id: int, message_ids: list) -> None:
    for mid in message_ids:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=mid)
        except Exception as e:
            logging.warning(f"Не удалось удалить сообщение {mid}: {e}")