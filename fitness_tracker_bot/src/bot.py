import asyncio
from aiogram import Bot, Dispatcher
import logging
from config import TOKEN
from handlers import router as main_router


async def main() -> None:
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    await dp.include_router(main_router)

    async with aiosqlite.connect("db.sqlite3") as db:
        await dp.start_polling(bot, db=db)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')