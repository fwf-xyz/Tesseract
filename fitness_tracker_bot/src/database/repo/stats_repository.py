from datetime import date, timedelta
import sqlite3

class UserRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    # def get_weekly_stats(self, user_id):
    #     cursor = self.conn.cursor()
    #     today = date.today()
    #     week_ago = today - timedelta(days=7)

    #     cursor.execute(
    #         """SELECT workout_type, duration, intensity, date
    #            FROM workouts
    #            WHERE user_id = ? AND date >= ?""",
    #         (user_id, week_ago)
    #     )
    #     return cursor.fetchall()