import sqlite3

class GoalRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save_goal(self, user_id: int, goal: str, deadline: str) -> None:
        with self.conn:
            self.conn.execute(
                """INSERT INTO goals
                (user_id, goal, deadline) 
                VALUES (?, ?, ?)""",
                (user_id, goal, deadline)
        )
            
    def get_latest_goal(self, user_id: int) -> sqlite3.Row | None:
        return self.conn.execute(
            """SELECT goal, deadline, status
            FROM goals
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
        (user_id,)
    ).fetchone()
