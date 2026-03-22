import sqlite3

class ProfileRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create_user_profile(self, user_id: int, age: int, gender: int, 
                    height: int,  weight: int, health_params: str | None) -> None:
        with self.conn:
            self.conn.execute(
                """INSERT INTO user_profiles
                (user_id, age, gender, height, weight, health_params) 
                VALUES (?, ?, ?, ?, ?, ?)""",
                (user_id, age, gender, height, weight, health_params)
        )
