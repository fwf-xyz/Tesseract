from aiogram import types, Router, F
from config import ADMIN_ID
from database import Repository


admin = ADMIN_ID
router = Router()


@router.message(F.photo or F.animation)
async def get_design_id(message: types.Message, repo: Repository):
    if message.from_user.id != ADMIN_ID:
        return

    cursor = repo.conn.cursor()

    file_id = message.photo[-1].file_id
    user_id = message.from_user.id
    content = message.caption
    created_at = message.date.strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute(
        """INSERT INTO file_ids (user_id, file_id, content, created_at) 
        VALUES (?, ?, ?, ?)
        ON CONFLICT(content) 
        DO UPDATE SET 
        user_id = excluded.user_id,
        file_id = excluded.file_id,
        created_at = excluded.created_at;""",
        (user_id, file_id, content, created_at)
    )

    repo.conn.commit()
    await message.answer("✅ Изображение по параметру успешно установлено!")






