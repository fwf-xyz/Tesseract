import asyncio
from aiogram import Bot, Dispatcher
import logging
from config import TOKEN
from handlers import router as main_router

from database import get_connection, init_db, Repository
from middlewares import RepoMiddleware

from jobs import deadline_scheduler


async def main():
    dp = Dispatcher()

    db_conn = get_connection()
    init_db(db_conn)
    repo = Repository(conn=db_conn)

    bot = Bot(token=TOKEN)

    dp.update.middleware(RepoMiddleware(repo=repo))
    dp.include_router(main_router)

    task = asyncio.create_task(deadline_scheduler(bot, repo))

    try:
        await dp.start_polling(bot)
    finally:
        task.cancel()
        await bot.session.close()
        db_conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
