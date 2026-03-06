import sqlite3

class WorkoutRepository:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.db.row_factory = sqlite3.Row

    def save_workout(self, user_id: int, workout_type: str, duration: int, 
                    intensity: str, note: str | None, created_at: str):
        cursor = self.db.cursor()
        cursor.execute(
            """INSERT INTO workouts (user_id, workout_type, duration, intensity, notes, created_at) 
            VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, workout_type, duration, intensity, note, created_at)
        )
        self.db.commit()

    def get_history(self, user_id: int, limit: int):
        cursor = self.db.cursor()
        cursor.execute(
            """SELECT created_at, workout_type, duration, intensity
            FROM workouts 
            WHERE user_id = ? 
            ORDER BY created_at DESC
            LIMIT ?""",
            (user_id, limit)
        )
        return cursor.fetchall()