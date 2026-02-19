"""
Database utility functions for the Mood Recommendation System.
Provides connection management and query helpers.
"""

import sqlite3
import os
from datetime import datetime

# Path to the SQLite database file
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "mood_recommendations.db")
SCHEMA_PATH = os.path.join(DB_DIR, "schema.sql")


def get_connection():
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn


def init_db():
    """Initialize the database by executing the schema SQL file."""
    conn = get_connection()
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


def get_songs_by_mood(mood_tag, limit=5):
    """
    Retrieve songs matching the given mood tag.
    Returns a randomized selection up to `limit` results.
    """
    conn = get_connection()
    cursor = conn.execute(
        "SELECT * FROM songs WHERE mood_tag = ? ORDER BY RANDOM() LIMIT ?",
        (mood_tag.lower(), limit),
    )
    songs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return songs


def get_movies_by_mood(mood_tag, limit=5):
    """
    Retrieve movies matching the given mood tag.
    Returns a randomized selection up to `limit` results.
    """
    conn = get_connection()
    cursor = conn.execute(
        "SELECT * FROM movies WHERE mood_tag = ? ORDER BY RANDOM() LIMIT ?",
        (mood_tag.lower(), limit),
    )
    movies = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return movies


def log_mood(cnn_emotion, cnn_confidence, questionnaire_mood,
             questionnaire_score, final_mood):
    """Log a mood analysis session to the mood_history table."""
    conn = get_connection()
    conn.execute(
        """INSERT INTO mood_history
           (timestamp, cnn_emotion, cnn_confidence, questionnaire_mood,
            questionnaire_score, final_mood)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            datetime.now().isoformat(),
            cnn_emotion,
            cnn_confidence,
            questionnaire_mood,
            questionnaire_score,
            final_mood,
        ),
    )
    conn.commit()
    conn.close()


def get_mood_history(limit=20):
    """Retrieve recent mood history entries."""
    conn = get_connection()
    cursor = conn.execute(
        "SELECT * FROM mood_history ORDER BY id DESC LIMIT ?", (limit,)
    )
    history = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return history
