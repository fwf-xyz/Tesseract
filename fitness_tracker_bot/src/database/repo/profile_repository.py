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
            

    def update_user_profile(self, user_id: int, age: int, gender: int, 
                height: int, weight: int, health_params: str | None) -> None:
        with self.conn:
            self.conn.execute(
                """UPDATE user_profiles
                SET age = ?, gender = ?, height = ?, weight = ?, health_params = ?
                WHERE user_id = ?""",
                (age, gender, height, weight, health_params, user_id)
            )
            
            
    def get_user_profile(self, user_id: int):
        result = self.conn.execute(
            """SELECT id, age, gender, height, weight, health_params, created_at
            FROM user_profiles
            WHERE user_id = ?
            """,
            (user_id,)
        ).fetchone()
        return dict(result) if result else None

