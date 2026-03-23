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
            """SELECT goal, deadline, status, created_at
            FROM goals
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
        (user_id,)
    ).fetchone()

    def get_goals_history(self, user_id: int) -> list[tuple]:
        return self.conn.execute(
            """SELECT goal, deadline, status, created_at
            FROM goals
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
        (user_id,)
    ).fetchall()


    # def change_goal_status(self, user_id: int):


    # cursor.execute(
    #     """INSERT INTO goals (status, completed_at) 
    #     VALUES (?, ?)
    #     ON CONFLICT(content) 
    #     DO UPDATE SET 
    #     user_id = excluded.user_id,
    #     file_id = excluded.file_id,
    #     created_at = excluded.created_at;""",
    #     (user_id, file_id, content, created_at)
    # )
