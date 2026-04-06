import sqlite3
from datetime import datetime

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


    def change_goal_status(self, user_id: int, new_status: str) -> None:
        completed_at = datetime.now()

        with self.conn:
            self.conn.execute("""
                UPDATE goals 
                SET status = ?, 
                    completed_at = ?
                WHERE id = (
                    SELECT id 
                    FROM goals 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT 1
                );
            """,
                (new_status, completed_at, user_id)
            )

    def get_overdue_goals(self, now: str) -> list[tuple]:
        return self.conn.execute(
            """
            SELECT id, user_id, goal, deadline, created_at
            FROM goals
            WHERE deadline <= ?
            AND status = 'in_progress'
            """,
            (now,)
        ).fetchall()


    def set_overdue_goal_statys(self, goal_id: int) -> None:
        with self.conn:
            self.conn.execute(
                """
                UPDATE goals
                SET status = 'overdue'
                WHERE id = ?
                """,
                (goal_id,)
            )


