"""
Mood Fusion Engine
Combines CNN emotion predictions with questionnaire scores using
a weighted decision logic to determine the final mood.
"""

MOOD_CATEGORIES = ["happy", "sad", "angry", "neutral", "excited", "stressed"]

# Default weights (configurable)
DEFAULT_CNN_WEIGHT = 0.6
DEFAULT_QUESTIONNAIRE_WEIGHT = 0.4


def fuse_moods(cnn_mood_scores=None, questionnaire_mood_scores=None,
               cnn_weight=DEFAULT_CNN_WEIGHT,
               questionnaire_weight=DEFAULT_QUESTIONNAIRE_WEIGHT):
    """
    Fuse CNN emotion scores and questionnaire scores into a final mood.

    Parameters
    ----------
    cnn_mood_scores : dict or None
        {mood: score} from the CNN (values should sum to ~1.0).
    questionnaire_mood_scores : dict or None
        {mood: score} from the questionnaire (values should sum to ~1.0).
    cnn_weight : float
        Weight for CNN predictions (default 0.6).
    questionnaire_weight : float
        Weight for questionnaire scores (default 0.4).

    Returns
    -------
    dict with keys:
        final_mood    : str   — The determined mood category
        final_scores  : dict  — {mood: fused_score} for all categories
        confidence    : float — Score of the top mood (0-1)
        cnn_used      : bool  — Whether CNN input was available
        quest_used    : bool  — Whether questionnaire input was available
    """
    cnn_used = cnn_mood_scores is not None and len(cnn_mood_scores) > 0
    quest_used = questionnaire_mood_scores is not None and len(questionnaire_mood_scores) > 0

    # Initialize fused scores
    fused = {mood: 0.0 for mood in MOOD_CATEGORIES}

    if cnn_used and quest_used:
        # Both inputs available — weighted combination
        for mood in MOOD_CATEGORIES:
            cnn_val = cnn_mood_scores.get(mood, 0.0)
            quest_val = questionnaire_mood_scores.get(mood, 0.0)
            fused[mood] = cnn_weight * cnn_val + questionnaire_weight * quest_val

    elif cnn_used:
        # Only CNN available — use full weight
        for mood in MOOD_CATEGORIES:
            fused[mood] = cnn_mood_scores.get(mood, 0.0)

    elif quest_used:
        # Only questionnaire available — use full weight
        for mood in MOOD_CATEGORIES:
            fused[mood] = questionnaire_mood_scores.get(mood, 0.0)

    else:
        # No input at all — default to neutral
        fused["neutral"] = 1.0

    # Normalize to sum to 1.0
    total = sum(fused.values())
    if total > 0:
        fused = {mood: score / total for mood, score in fused.items()}

    # Determine final mood
    final_mood = max(fused, key=fused.get)
    confidence = fused[final_mood]

    return {
        "final_mood": final_mood,
        "final_scores": fused,
        "confidence": confidence,
        "cnn_used": cnn_used,
        "quest_used": quest_used,
    }
