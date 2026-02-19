"""
Questionnaire Scorer
Aggregates mood scores from all questionnaire responses into a final mood profile.
"""

from questionnaire.questions import MOOD_CATEGORIES, get_question


def score_responses(responses):
    """
    Calculate aggregated mood scores from a list of questionnaire responses.

    Parameters
    ----------
    responses : list of dict
        Each dict has:
            "question_id" : str  — ID of the question answered
            "option_index" : int — Index of the chosen option (0-based)

    Returns
    -------
    dict with keys:
        mood_scores : dict  — {mood: normalized_score} for all 6 categories
        top_mood    : str   — The mood with the highest score
        raw_scores  : dict  — {mood: raw_accumulated_score} before normalization
    """
    # Accumulate raw scores
    raw_scores = {mood: 0.0 for mood in MOOD_CATEGORIES}

    for response in responses:
        question = get_question(response["question_id"])
        if question is None:
            continue

        option_idx = response["option_index"]
        if option_idx < 0 or option_idx >= len(question["options"]):
            continue

        option = question["options"][option_idx]
        for mood, score in option.get("mood_scores", {}).items():
            raw_scores[mood] += score

    # Normalize scores to sum to 1.0
    total = sum(raw_scores.values())
    if total > 0:
        mood_scores = {mood: score / total for mood, score in raw_scores.items()}
    else:
        # Uniform distribution as fallback
        mood_scores = {mood: 1.0 / len(MOOD_CATEGORIES) for mood in MOOD_CATEGORIES}

    # Determine top mood
    top_mood = max(mood_scores, key=mood_scores.get)

    return {
        "mood_scores": mood_scores,
        "top_mood": top_mood,
        "raw_scores": raw_scores,
    }
