from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import TelegramObject

from database import Repository

class RepoMiddleware(BaseMiddleware):
    def __init__(self, repo: Repository):
        super().__init__()
        self.repo = repo

    async def __call__(self,
                    handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                    event: TelegramObject,
                    data: Dict[str, Any]) -> Any:
        data["repo"] = self.repo
        return await handler(event, data)