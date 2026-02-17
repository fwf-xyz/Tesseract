import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот на aiogram 3.x")

@dp.message()
async def echo_message(message: types.Message):
    await message.answer(f"Вы написали: {message.text}")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())