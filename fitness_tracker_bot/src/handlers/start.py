from aiogram import Router, types
from aiogram.filters import Command
import logging

router = Router()

@router.message(Command('start'))
async def start_cmd(message: types.Message):
    username = message.from_user.username or "No username"
    logging.info(f"  User: @{username} (ID: {message.from_user.id}) нажал на /start")
    await message.answer("Привет!")













