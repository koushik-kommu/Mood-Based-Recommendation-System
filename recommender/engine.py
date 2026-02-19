"""
Recommendation Engine
Retrieves mood-matched songs and movies from the database.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_utils import get_songs_by_mood, get_movies_by_mood, log_mood


def get_recommendations(final_mood, cnn_emotion=None, cnn_confidence=None,
                        questionnaire_mood=None, questionnaire_score=None,
                        num_songs=5, num_movies=5):
    """
    Get song and movie recommendations for a given mood.

    Parameters
    ----------
    final_mood : str
        The fused mood category.
    cnn_emotion : str, optional
        Raw CNN emotion label for logging.
    cnn_confidence : float, optional
        CNN confidence score for logging.
    questionnaire_mood : str, optional
        Questionnaire top mood for logging.
    questionnaire_score : float, optional
        Questionnaire top score for logging.
    num_songs : int
        Number of songs to recommend.
    num_movies : int
        Number of movies to recommend.

    Returns
    -------
    dict with keys:
        mood   : str
        songs  : list of dict
        movies : list of dict
    """

    # Fetch recommendations from database
    songs = get_songs_by_mood(final_mood, limit=num_songs)
    movies = get_movies_by_mood(final_mood, limit=num_movies)

    # Log the mood analysis session
    try:
        log_mood(
            cnn_emotion=cnn_emotion,
            cnn_confidence=cnn_confidence,
            questionnaire_mood=questionnaire_mood,
            questionnaire_score=questionnaire_score,
            final_mood=final_mood,
        )
    except Exception as e:
        print(f"Warning: Could not log mood history: {e}")

    return {
        "mood": final_mood,
        "songs": songs,
        "movies": movies,
    }
