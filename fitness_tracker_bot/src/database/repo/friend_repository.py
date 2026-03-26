import sqlite3

class FriendRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def get_friends_list(self, user_id: int) -> list:
        return self.conn.execute("""
            SELECT u.user_id, u.username, f.created_at AS created_at
            FROM friends f
            JOIN users u ON u.user_id = f.receiver_id
            WHERE f.requester_id = ? AND f.status = 'accepted'

            UNION

            SELECT u.user_id, u.username, f.created_at AS created_at
            FROM friends f
            JOIN users u ON u.user_id = f.requester_id
            WHERE f.receiver_id = ? AND f.status = 'accepted'

            ORDER BY created_at DESC
    """, (user_id, user_id)).fetchall()