"""
Mood Fusion Engine
Combines CNN emotion predictions with questionnaire scores.
Supports 10 mood categories.
"""

MOOD_CATEGORIES = [
    "happy", "sad", "angry", "neutral", "excited", "stressed", "calm",
]

DEFAULT_CNN_WEIGHT = 0.5
DEFAULT_QUESTIONNAIRE_WEIGHT = 0.5


def fuse_moods(cnn_mood_scores=None, questionnaire_mood_scores=None,
               cnn_weight=DEFAULT_CNN_WEIGHT,
               questionnaire_weight=DEFAULT_QUESTIONNAIRE_WEIGHT):
    """
    Fuse CNN emotion scores and questionnaire scores into a final mood.
    """
    cnn_used = cnn_mood_scores is not None and len(cnn_mood_scores) > 0
    quest_used = questionnaire_mood_scores is not None and len(questionnaire_mood_scores) > 0

    fused = {mood: 0.0 for mood in MOOD_CATEGORIES}

    if cnn_used and quest_used:
        for mood in MOOD_CATEGORIES:
            cnn_val = cnn_mood_scores.get(mood, 0.0)
            quest_val = questionnaire_mood_scores.get(mood, 0.0)
            fused[mood] = cnn_weight * cnn_val + questionnaire_weight * quest_val
    elif cnn_used:
        for mood in MOOD_CATEGORIES:
            fused[mood] = cnn_mood_scores.get(mood, 0.0)
    elif quest_used:
        for mood in MOOD_CATEGORIES:
            fused[mood] = questionnaire_mood_scores.get(mood, 0.0)
    else:
        fused["neutral"] = 1.0

    total = sum(fused.values())
    if total > 0:
        fused = {mood: score / total for mood, score in fused.items()}

    final_mood = max(fused, key=fused.get)
    confidence = fused[final_mood]

    return {
        "final_mood": final_mood,
        "final_scores": fused,
        "confidence": confidence,
        "cnn_used": cnn_used,
        "quest_used": quest_used,
    }
