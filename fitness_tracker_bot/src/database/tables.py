CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    username    TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    consent_version TEXT NOT NULL DEFAULT '1.0'
);
"""

CREATE_WORKOUTS_TABLE = """
CREATE TABLE IF NOT EXISTS workouts (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL,
    workout_type TEXT NOT NULL,
    duration     INTEGER NOT NULL,
    intensity    INTEGER NOT NULL,
    notes        TEXT,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
"""

CREATE_GOALS_TABLE = """
CREATE TABLE IF NOT EXISTS goals (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL,
    goal          TEXT NOT NULL,
    status        TEXT NOT NULL DEFAULT 'in_progress',
    deadline      TIMESTAMP NOT NULL,
    completed_at  TIMESTAMP,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
"""

CREATE_FRIENDS_TABLE = """
CREATE TABLE IF NOT EXISTS friends (
    id                       INTEGER PRIMARY KEY AUTOINCREMENT,
    requester_id             INTEGER NOT NULL,
    receiver_id              INTEGER NOT NULL,
    status                   TEXT    NOT NULL DEFAULT 'pending'
                                CHECK(status IN ('pending', 'accepted', 'declined')),
    notification_status  INTEGER DEFAULT 1,
    created_at               TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (requester_id, receiver_id),
    FOREIGN KEY (requester_id) REFERENCES users(user_id),
    FOREIGN KEY (receiver_id)  REFERENCES users(user_id)
);
"""

CREATE_FILEID_TABLE = """
CREATE TABLE IF NOT EXISTS file_ids (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER NOT NULL,
    file_id        TEXT NOT NULL,
    content        TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
"""

CREATE_AI_SUMMARIES_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS ai_summaries_history (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER NOT NULL,
    summary_text   TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
"""

CREATE_USER_PROFILES_TABLE = """
CREATE TABLE IF NOT EXISTS user_profiles (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER NOT NULL,
    age            INTEGER NOT NULL,
    gender         TEXT NOT NULL,
    height         INTEGER NOT NULL,
    weight         INTEGER NOT NULL,
    health_params  TEXT,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
"""


ALL_TABLES = [
    CREATE_USERS_TABLE,
    CREATE_WORKOUTS_TABLE,
    CREATE_GOALS_TABLE,
    CREATE_FRIENDS_TABLE,
    CREATE_FILEID_TABLE,
    CREATE_AI_SUMMARIES_HISTORY_TABLE,
    CREATE_USER_PROFILES_TABLE
]