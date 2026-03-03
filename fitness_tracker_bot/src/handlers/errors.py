from aiogram import Router
from aiogram.types import ErrorEvent
from aiogram.exceptions import TelegramForbiddenError


router = Router()


@router.errors()
async def error_handler(event: ErrorEvent):
    if isinstance(event.exception, TelegramForbiddenError):
        return True
    
    print(f"Произошла ошибка: {event.exception}")
    
    raise event.exception