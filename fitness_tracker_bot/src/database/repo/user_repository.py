import sqlite3

class UserRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add_user(self, user_id, username):
        cursor = self.conn.cursor()
        cursor.execute(
                """INSERT OR IGNORE INTO users (user_id, username)
                VALUES (?, ?)""",
                (user_id, username)
            )

        self.conn.commit()

    def paste_decoration_id(self, content_name: str) -> str | None:
        cursor = self.conn.cursor()

        cursor.execute(
            "SELECT file_id FROM file_ids WHERE content = ?",
            (content_name,)
        )
        result = cursor.fetchone()

        return result[0] if result else None