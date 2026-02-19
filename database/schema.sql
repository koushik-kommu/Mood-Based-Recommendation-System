-- ============================================================
-- Mood-Based Song & Movie Recommendation System
-- Database Schema
-- ============================================================

-- Songs table: stores song metadata with mood tags and YouTube links
CREATE TABLE IF NOT EXISTS songs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT    NOT NULL,
    artist      TEXT    NOT NULL,
    genre       TEXT    NOT NULL,
    mood_tag    TEXT    NOT NULL,   -- happy | sad | angry | neutral | excited | stressed
    youtube_url TEXT    NOT NULL
);

-- Movies table: stores movie metadata with mood tags and OTT links
CREATE TABLE IF NOT EXISTS movies (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    title        TEXT    NOT NULL,
    genre        TEXT    NOT NULL,
    year         INTEGER NOT NULL,
    mood_tag     TEXT    NOT NULL,  -- happy | sad | angry | neutral | excited | stressed
    ott_platform TEXT    NOT NULL,  -- Netflix, Prime Video, Disney+ Hotstar, etc.
    ott_url      TEXT    NOT NULL
);

-- Mood history table: logs each user session's mood analysis
CREATE TABLE IF NOT EXISTS mood_history (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp            TEXT    NOT NULL,
    cnn_emotion          TEXT,
    cnn_confidence       REAL,
    questionnaire_mood   TEXT,
    questionnaire_score  REAL,
    final_mood           TEXT    NOT NULL
);

-- Indexes for fast mood-based queries
CREATE INDEX IF NOT EXISTS idx_songs_mood  ON songs(mood_tag);
CREATE INDEX IF NOT EXISTS idx_movies_mood ON movies(mood_tag);
