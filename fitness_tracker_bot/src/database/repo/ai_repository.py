import sqlite3
from datetime import date, timedelta

class AIRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def get_ai_history(self, user_id: int, days_back: int):
        since_date = date.today() - timedelta(days=days_back)

        rows = self.conn.execute(
            """SELECT id, summary_text, created_at
            FROM ai_summaries_history
            WHERE user_id = ? AND created_at >= ?
            ORDER BY created_at DESC
            """,
            (user_id, since_date)
        ).fetchall()

        return [dict(row) for row in rows]
    

    def save_ai_summary(self, user_id: int, summary_text: str) -> None:
        with self.conn:
            self.conn.execute(
                """INSERT INTO ai_summaries_history 
                (user_id, summary_text) 
                VALUES
                (?, ?)""",
                (user_id, summary_text)
            )