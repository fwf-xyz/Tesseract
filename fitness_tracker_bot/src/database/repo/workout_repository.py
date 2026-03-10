from datetime import date, timedelta
import sqlite3

class WorkoutRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.conn.row_factory = sqlite3.Row


    def save_workout(self, user_id: int, workout_type: str, duration: int, 
                    intensity: str, note: str | None, created_at: str):
        cursor = self.conn.cursor()
        cursor.execute(
            """INSERT INTO workouts (user_id, workout_type, duration, intensity, notes, created_at) 
            VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, workout_type, duration, intensity, note, created_at)
        )
        self.conn.commit()


    def get_history(self, user_id: int, start_limit: int):
        cursor = self.conn.cursor()

        query = """SELECT created_at, workout_type, duration, intensity
            FROM workouts 
            WHERE user_id = ?  and created_at >= ?
            ORDER BY created_at DESC
            """
        start_date = date.today() - timedelta(days=start_limit)
        cursor.execute(query, (user_id, start_date))
        return cursor.fetchall()
