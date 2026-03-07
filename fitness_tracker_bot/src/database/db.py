import sqlite3
from .tables import ALL_TABLES 
from config import db_path

DB_PATH = db_path

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
