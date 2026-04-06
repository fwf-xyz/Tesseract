import sqlite3
from typing import Optional

class FriendRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn


    def _execute(self, query: str, params: tuple = ()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor


    def add_friend_request(self, requester_id: int, receiver_id: int, message_id: int = None) -> bool:
        query = """
            INSERT
            INTO friends (requester_id, receiver_id, status)
            VALUES (?, ?, ?), (?, ?, ?)
        """
        result = self._execute(query, (requester_id, receiver_id, 'accepted',
                                        receiver_id, requester_id, 'accepted'))
        return result.rowcount == 2


    def get_relationship_status(self, user1: int, user2: int) -> Optional[str]:
        query = """
            SELECT status FROM friends
            WHERE requester_id = ? AND receiver_id = ?
        """
        res = self._execute(query, (user1, user2)).fetchone()
        return res[0] if res else None


    def accept_friend_request(self, requester_id: int, receiver_id: int):
        query = """
            UPDATE friends
            SET status = 'accepted', updated_at = CURRENT_TIMESTAMP
            WHERE (requester_id = ? AND receiver_id = ?)
            OR (requester_id = ? AND receiver_id = ?)
        """
        self._execute(query, (requester_id, receiver_id, receiver_id, requester_id))


    def delete_friendship(self, user1: int, user2: int):
        query = """
            DELETE FROM friends
            WHERE (requester_id = ? AND receiver_id = ?)
            OR (requester_id = ? AND receiver_id = ?)
        """
        self._execute(query, (user1, user2, user2, user1))


    def get_friends_list(self, user_id: int) -> list[sqlite3.Row]:
        return self.conn.execute("""
            SELECT receiver_id, created_at
            FROM friends
            WHERE requester_id = ? AND status = ?
            ORDER BY created_at DESC
        """,
        (user_id, 'accepted')
        ).fetchall()


    def get_notification_status(self, requester_id: int, receiver_id: int) -> bool:
        query = """
            SELECT notification_status
            FROM friends
            WHERE requester_id = ? AND receiver_id = ?
        """
        res = self._execute(query, (requester_id, receiver_id)).fetchone()
        return bool(res[0]) if res else False

    
    def set_notification_status(self, requester_id: int, receiver_id: int, status: bool):
        query = """
            UPDATE friends
            SET notification_status = ?
            WHERE requester_id = ? AND receiver_id = ?
        """
        self._execute(query, (int(status), requester_id, receiver_id))