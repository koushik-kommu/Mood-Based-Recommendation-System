"""
Recommendation Engine — Weighted Scoring
Retrieves mood-matched songs and movies with auto language prioritization.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_utils import get_ranked_songs, get_ranked_movies, log_mood


def get_recommendations(final_mood, user_id=None,
                        cnn_emotion=None, cnn_confidence=None,
                        questionnaire_mood=None, questionnaire_score=None,
                        num_songs=10, num_movies=10, **kwargs):
    """Get ranked song and movie recommendations for a given mood."""
    songs = get_ranked_songs(final_mood, limit=num_songs)
    movies = get_ranked_movies(final_mood, limit=num_movies)

    try:
        log_mood(
            cnn_emotion=cnn_emotion,
            cnn_confidence=cnn_confidence,
            questionnaire_mood=questionnaire_mood,
            questionnaire_score=questionnaire_score,
            final_mood=final_mood,
            user_id=user_id,
        )
    except Exception as e:
        print(f"Warning: Could not log mood history: {e}")

    return {"mood": final_mood, "songs": songs, "movies": movies}
