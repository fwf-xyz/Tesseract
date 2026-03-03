import sqlite3
from .tables import ALL_TABLES 

DB_PATH = "fitness.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        for query in ALL_TABLES:
            cursor.execute(query)
        conn.commit()


def paste_decoration_id(content_name, db: sqlite3.Connection) -> str | None:
    cursor = db.cursor()

    cursor.execute(
        "SELECT file_id FROM file_ids WHERE content = ?",
        (content_name,)
    )
    result = cursor.fetchone()

    return result[0] if result else None