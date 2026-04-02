import sqlite3
import os
import random
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "mood_recommendations.db")
SCHEMA_PATH = os.path.join(DB_DIR, "schema.sql")

# Language priority weights (Telugu-first)
LANGUAGE_WEIGHTS = {
    "Telugu": 5.0,
    "English": 4.0,
    "Hindi": 3.0,
    "Tamil": 3.0,
    "Kannada": 2.0,
    "Malayalam": 2.0,
    "Bengali": 2.0,
    "Marathi": 2.0,
    "Punjabi": 2.0,
}
DEFAULT_LANG_WEIGHT = 1.0

# Diversity jitter: random score perturbation range [0, JITTER_RANGE]
# Higher = more diversity, lower = more deterministic ranking
DIVERSITY_JITTER = 0.25
# Pool multiplier: fetch this many times more items than needed
POOL_MULTIPLIER = 3


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


# ── Weighted Recommendation Queries ──────────────────────────────

def _score_item(item, mood_tag):
    """Compute weighted score for a song/movie item."""
    lang = item.get("language", "")
    lang_w = LANGUAGE_WEIGHTS.get(lang, DEFAULT_LANG_WEIGHT)
    popularity = item.get("popularity", 5.0)
    rating = item.get("rating", 5.0)

    # Mood is already matched (filtered by SQL), so mood_match = 1.0
    score = (1.0 * 1.0) + (lang_w / 5.0 * 0.3) + (popularity / 10.0 * 0.15) + (rating / 10.0 * 0.05)
    return score


def _diverse_select(items, mood_tag, limit):
    """
    Stochastic diversity sampling:
    1. Score all items deterministically
    2. Take a larger pool (POOL_MULTIPLIER × limit)
    3. Add random jitter to each score
    4. Re-sort by jittered score and return top `limit`

    This ensures high-quality matches while rotating recommendations
    so users rarely see the exact same results twice.
    """
    for item in items:
        item["_base_score"] = _score_item(item, mood_tag)

    # Sort by base score first
    items.sort(key=lambda x: x["_base_score"], reverse=True)

    # Take a wider pool
    pool_size = min(len(items), limit * POOL_MULTIPLIER)
    pool = items[:pool_size]

    # Add random jitter to diversify
    for item in pool:
        item["_jittered"] = item["_base_score"] + random.uniform(0, DIVERSITY_JITTER)

    # Re-sort by jittered score
    pool.sort(key=lambda x: x["_jittered"], reverse=True)

    # Take top N and clean up internal keys
    result = pool[:limit]
    for item in result:
        item.pop("_base_score", None)
        item.pop("_jittered", None)

    return result


def get_ranked_songs(mood_tag, limit=10):
    """Retrieve mood-matched songs with stochastic diversity sampling."""
    conn = get_connection()
    cursor = conn.execute(
        "SELECT * FROM songs WHERE mood_tag = ?", (mood_tag.lower(),)
    )
    songs = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return _diverse_select(songs, mood_tag, limit)


def get_ranked_movies(mood_tag, limit=10):
    """Retrieve mood-matched movies with stochastic diversity sampling."""
    conn = get_connection()
    cursor = conn.execute(
        "SELECT * FROM movies WHERE mood_tag = ?", (mood_tag.lower(),)
    )
    movies = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return _diverse_select(movies, mood_tag, limit)


# Legacy compat wrappers
def get_songs_by_mood(mood_tag, languages=None, limit=10):
    return get_ranked_songs(mood_tag, limit)

def get_movies_by_mood(mood_tag, languages=None, limit=10):
    return get_ranked_movies(mood_tag, limit)


# ── Mood History ────────────────────────────────────────────────

def log_mood(cnn_emotion, cnn_confidence, questionnaire_mood,
             questionnaire_score, final_mood, user_id=None):
    conn = get_connection()
    conn.execute(
        """INSERT INTO mood_history
           (user_id, timestamp, cnn_emotion, cnn_confidence,
            questionnaire_mood, questionnaire_score, final_mood)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (user_id, datetime.now().isoformat(), cnn_emotion, cnn_confidence,
         questionnaire_mood, questionnaire_score, final_mood),
    )
    conn.commit()
    conn.close()


def get_mood_history(limit=20):
    conn = get_connection()
    cursor = conn.execute(
        "SELECT * FROM mood_history ORDER BY id DESC LIMIT ?", (limit,)
    )
    history = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return history


def get_user_mood_history(user_id, limit=20):
    conn = get_connection()
    cursor = conn.execute(
        "SELECT * FROM mood_history WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit),
    )
    history = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return history


# ── User Authentication ─────────────────────────────────────────

def create_user(username, email, password):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, generate_password_hash(password)),
        )
        conn.commit()
        user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.close()
        return {"id": user_id, "username": username, "email": email}
    except sqlite3.IntegrityError:
        conn.close()
        return None


def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def verify_user(username, password):
    user = get_user_by_username(username)
    if user and check_password_hash(user["password_hash"], password):
        return user
    return None
