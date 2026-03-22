import sqlite3

class UserRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn


    def exists_user(self, user_id: int) -> bool:
        with self.conn:
            cursor = self.conn.execute(
                "SELECT EXISTS (SELECT 1 FROM users WHERE user_id = ?)", (user_id,)
            )
            return bool(cursor.fetchone()[0])


    def add_user(self, user_id, username) -> None:
        with self.conn:
            self.conn.execute(
                """INSERT OR IGNORE INTO users (user_id, username)
                VALUES (?, ?)""",
                (user_id, username)
            )


    def paste_decoration_id(self, content_name: str) -> str | None:
        cursor = self.conn.cursor()

        cursor.execute(
            "SELECT file_id FROM file_ids WHERE content = ?",
            (content_name,)
        )
        result = cursor.fetchone()

        return result[0] if result else None