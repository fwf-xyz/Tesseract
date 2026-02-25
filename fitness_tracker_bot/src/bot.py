import asyncio
from aiogram import Bot, Dispatcher
import logging
from config import TOKEN
from handlers import router as main_router

from database import get_connection, init_db
from middlewares import DbSessionMiddleware

from aiogram.exceptions import TelegramForbiddenError


async def main():
    dp = Dispatcher()
    init_db() 
    db_conn = get_connection()

    bot = Bot(token=TOKEN)
    dp.update.middleware(DbSessionMiddleware(connector=db_conn))
    dp.include_router(main_router)

    @dp.errors()
    async def error_handler(update, exception):
        if isinstance(exception, TelegramForbiddenError):
            return True
        raise exception

    try:
        await dp.start_polling(bot)
    finally:
        db_conn.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')