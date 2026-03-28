import sqlite3
from typing import List, Dict, Optional

class FriendRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _execute(self, query: str, params: tuple = ()):
    # Мы не вызываем connect(), а просто берем курсор у существующего соединения
        cursor = self.db_path.cursor() 
        cursor.execute(query, params)
        self.db_path.commit() # Не забываем коммитить изменения
        return cursor


    def add_friend_request(self, requester_id: int, receiver_id: int, message_id: int = None) -> bool:
        query = """
        INSERT OR IGNORE INTO friends (requester_id, receiver_id, notification_message_id, status)
        VALUES (?, ?, ?, 'pending')
        """
        result = self._execute(query, (requester_id, receiver_id, message_id))
        return result.rowcount > 0


    def get_relationship_status(self, user1: int, user2: int) -> Optional[str]:
        query = """
        SELECT status FROM friends 
        WHERE (requester_id = ? AND receiver_id = ?) 
        OR (requester_id = ? AND receiver_id = ?)
        """
        res = self._execute(query, (user1, user2, user2, user1)).fetchone()
        return res[0] if res else None


    def accept_friend_request(self, requester_id: int, receiver_id: int):
        query = """
        UPDATE friends 
        SET status = 'accepted', updated_at = CURRENT_TIMESTAMP 
        WHERE requester_id = ? AND receiver_id = ?
        """
        self._execute(query, (requester_id, receiver_id))


    def delete_friendship(self, user1: int, user2: int):
        query = """
        DELETE FROM friends 
        WHERE (requester_id = ? AND receiver_id = ?) 
        OR (requester_id = ? AND receiver_id = ?)
        """
        self._execute(query, (user1, user2, user2, user1))


    def get_friends_list(self, user_id: int) -> List[Dict]:
        query = """
        SELECT 
            CASE 
                WHEN f.requester_id = ? THEN f.receiver_id 
                ELSE f.requester_id 
            END as friend_id,
            u.username
        FROM friends f
        JOIN users u ON u.user_id = friend_id
        WHERE (f.requester_id = ? OR f.receiver_id = ?) 
        AND f.status = 'accepted'
        """
        res = self._execute(query, (user_id, user_id, user_id)).fetchall()
        return [{"id": row[0], "username": row[1]} for row in res]


    def get_notification_id(self, requester_id: int, receiver_id: int) -> Optional[int]:
        query = """
        SELECT notification_message_id FROM friends 
        WHERE requester_id = ? AND receiver_id = ?
        """
        res = self._execute(query, (requester_id, receiver_id)).fetchone()
        return res[0] if res else None