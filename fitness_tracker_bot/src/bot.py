import asyncio
from aiogram import Bot, Dispatcher
import logging
from config import TOKEN
from handlers import router as main_router

from database import get_connection, init_db
from middlewares import RepoMiddleware


async def main():
    dp = Dispatcher()
    db_conn = get_connection()
    init_db() 

    bot = Bot(token=TOKEN)
    dp.update.middleware(RepoMiddleware(conn=db_conn))
    dp.include_router(main_router)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        db_conn.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')