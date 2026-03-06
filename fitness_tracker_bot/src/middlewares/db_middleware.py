from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import TelegramObject
import sqlite3

from database import Repository

class RepoMiddleware(BaseMiddleware):
    def __init__(self, conn: sqlite3.Connection):
        super().__init__()
        self.conn = conn

    async def __call__(self,
                    handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                    event: TelegramObject,
                    data: Dict[str, Any]) -> Any:
        repo = Repository(self.conn)
        
        data["repo"] = repo

        return await handler(event, data)