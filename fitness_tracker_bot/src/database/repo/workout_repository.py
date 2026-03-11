from datetime import date, timedelta
import sqlite3

class WorkoutRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.conn.row_factory = sqlite3.Row


    def save_workout(self, user_id: int, workout_type: str, duration: int, 
                    intensity: str, note: str | None, created_at: str) -> None:
        with self.conn:
            self.conn.execute(
                """INSERT INTO workouts (user_id, workout_type, duration, intensity, notes, created_at) 
                VALUES (?, ?, ?, ?, ?, ?)""",
                (user_id, workout_type, duration, intensity, note, created_at)
            )


    def get_history(self, user_id: int, days_back: int) -> list[sqlite3.Row]:
        since = date.today() - timedelta(days=days_back)

        return self.conn.execute(
            """SELECT created_at, workout_type, duration, intensity
            FROM workouts 
            WHERE user_id = ? AND created_at >= ?
            ORDER BY created_at DESC
            """,
            (user_id, since)
        ).fetchall()
