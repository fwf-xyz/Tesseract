from aiogram import Router
from aiogram.types import ErrorEvent
from aiogram.exceptions import TelegramForbiddenError
from aiogram.exceptions import TelegramBadRequest

router = Router()


@router.errors()
async def error_handler(event: ErrorEvent):
    if isinstance(event.exception, TelegramForbiddenError):
        return True
    
    if isinstance(event.exception, TelegramBadRequest):
        if "message to delete not found" in str(event.exception):
            return True
    
    print(f"Произошла ошибка: {event.exception}")
    raise event.exception