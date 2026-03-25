-- ============================================================
-- Mood-Based Song & Movie Recommendation System
-- Database Schema v3 — Large-scale with weighted scoring
-- ============================================================

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE,
    email         TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS songs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT    NOT NULL,
    artist      TEXT    NOT NULL,
    genre       TEXT    NOT NULL,
    mood_tag    TEXT    NOT NULL,
    language    TEXT    NOT NULL DEFAULT 'Telugu',
    rating      REAL    NOT NULL DEFAULT 0.0,
    popularity  REAL    NOT NULL DEFAULT 5.0,
    youtube_url TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS movies (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    title        TEXT    NOT NULL,
    genre        TEXT    NOT NULL,
    year         INTEGER NOT NULL,
    mood_tag     TEXT    NOT NULL,
    language     TEXT    NOT NULL DEFAULT 'Telugu',
    rating       REAL    NOT NULL DEFAULT 0.0,
    popularity   REAL    NOT NULL DEFAULT 5.0,
    ott_platform TEXT    NOT NULL DEFAULT 'YouTube',
    ott_url      TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS mood_history (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id              INTEGER,
    timestamp            TEXT    NOT NULL,
    cnn_emotion          TEXT,
    cnn_confidence       REAL,
    questionnaire_mood   TEXT,
    questionnaire_score  REAL,
    final_mood           TEXT    NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_songs_mood     ON songs(mood_tag);
CREATE INDEX IF NOT EXISTS idx_movies_mood    ON movies(mood_tag);
CREATE INDEX IF NOT EXISTS idx_songs_lang     ON songs(language);
CREATE INDEX IF NOT EXISTS idx_movies_lang    ON movies(language);
CREATE INDEX IF NOT EXISTS idx_history_user   ON mood_history(user_id);
