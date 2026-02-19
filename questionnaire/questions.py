"""
Dynamic Questionnaire Module
Adaptive question tree where follow-up questions depend on previous answers.
Each answer carries mood scores that accumulate into a final mood profile.
"""

# ── Mood Categories ──────────────────────────────────────────────────────
MOOD_CATEGORIES = ["happy", "sad", "angry", "neutral", "excited", "stressed"]

# ── Question Tree ────────────────────────────────────────────────────────
# Structure:
#   Each question has an "id", "text", list of "options".
#   Each option has "text", "mood_scores" dict, and optional "next_question_id".
#   If "next_question_id" is None, the questionnaire ends after that option.

QUESTIONS = {
    "q1": {
        "id": "q1",
        "text": "How would you describe your overall energy level right now?",
        "options": [
            {
                "text": "Very high — I feel like I could conquer the world!",
                "mood_scores": {"happy": 0.3, "excited": 0.7},
                "next_question_id": "q2_high_energy",
            },
            {
                "text": "Moderate — I feel pretty balanced",
                "mood_scores": {"neutral": 0.6, "happy": 0.2},
                "next_question_id": "q2_moderate",
            },
            {
                "text": "Low — I feel drained or tired",
                "mood_scores": {"sad": 0.4, "stressed": 0.3},
                "next_question_id": "q2_low_energy",
            },
            {
                "text": "Agitated — I feel restless or irritated",
                "mood_scores": {"angry": 0.5, "stressed": 0.3},
                "next_question_id": "q2_agitated",
            },
        ],
    },

    # ── Branch: High Energy ──────────────────────────────────────────
    "q2_high_energy": {
        "id": "q2_high_energy",
        "text": "What's driving your energy right now?",
        "options": [
            {
                "text": "Something exciting happened / is about to happen",
                "mood_scores": {"excited": 0.6, "happy": 0.3},
                "next_question_id": "q3_excited",
            },
            {
                "text": "I'm just in a great mood for no particular reason",
                "mood_scores": {"happy": 0.7, "excited": 0.2},
                "next_question_id": "q3_happy",
            },
            {
                "text": "Nervous energy — I have too much on my plate",
                "mood_scores": {"stressed": 0.5, "excited": 0.2},
                "next_question_id": "q3_stressed",
            },
        ],
    },

    # ── Branch: Moderate Energy ──────────────────────────────────────
    "q2_moderate": {
        "id": "q2_moderate",
        "text": "What are you in the mood for right now?",
        "options": [
            {
                "text": "Something fun and upbeat",
                "mood_scores": {"happy": 0.5, "excited": 0.3},
                "next_question_id": "q3_happy",
            },
            {
                "text": "Something calm and peaceful",
                "mood_scores": {"neutral": 0.5, "stressed": 0.2},
                "next_question_id": "q3_neutral",
            },
            {
                "text": "Something deep and emotional",
                "mood_scores": {"sad": 0.4, "neutral": 0.3},
                "next_question_id": "q3_sad",
            },
        ],
    },

    # ── Branch: Low Energy ───────────────────────────────────────────
    "q2_low_energy": {
        "id": "q2_low_energy",
        "text": "What best describes why you feel this way?",
        "options": [
            {
                "text": "I'm going through a tough time",
                "mood_scores": {"sad": 0.6, "stressed": 0.2},
                "next_question_id": "q3_sad",
            },
            {
                "text": "I'm just tired and want to relax",
                "mood_scores": {"neutral": 0.4, "stressed": 0.3},
                "next_question_id": "q3_neutral",
            },
            {
                "text": "I feel lonely or disconnected",
                "mood_scores": {"sad": 0.7},
                "next_question_id": "q3_sad",
            },
        ],
    },

    # ── Branch: Agitated ─────────────────────────────────────────────
    "q2_agitated": {
        "id": "q2_agitated",
        "text": "What's making you feel this way?",
        "options": [
            {
                "text": "Someone or something upset me",
                "mood_scores": {"angry": 0.6, "stressed": 0.2},
                "next_question_id": "q3_angry",
            },
            {
                "text": "Work or study pressure",
                "mood_scores": {"stressed": 0.6, "angry": 0.2},
                "next_question_id": "q3_stressed",
            },
            {
                "text": "I feel frustrated with myself",
                "mood_scores": {"angry": 0.3, "sad": 0.3, "stressed": 0.2},
                "next_question_id": "q3_angry",
            },
        ],
    },

    # ── Level 3 Questions ────────────────────────────────────────────
    "q3_happy": {
        "id": "q3_happy",
        "text": "How do you feel about spending time with others right now?",
        "options": [
            {
                "text": "I'd love to be around people!",
                "mood_scores": {"happy": 0.5, "excited": 0.3},
                "next_question_id": "q4_social",
            },
            {
                "text": "I'm happy on my own too",
                "mood_scores": {"happy": 0.4, "neutral": 0.3},
                "next_question_id": "q4_solo",
            },
        ],
    },

    "q3_sad": {
        "id": "q3_sad",
        "text": "Would you prefer something to cheer you up or match your mood?",
        "options": [
            {
                "text": "Cheer me up — I want to feel better",
                "mood_scores": {"happy": 0.3, "sad": 0.2},
                "next_question_id": "q4_social",
            },
            {
                "text": "Match my mood — I want to feel understood",
                "mood_scores": {"sad": 0.6},
                "next_question_id": "q4_solo",
            },
        ],
    },

    "q3_angry": {
        "id": "q3_angry",
        "text": "What would help you feel better right now?",
        "options": [
            {
                "text": "Something intense to let it out",
                "mood_scores": {"angry": 0.5, "excited": 0.2},
                "next_question_id": "q4_intense",
            },
            {
                "text": "Something calming to cool down",
                "mood_scores": {"stressed": 0.3, "neutral": 0.3},
                "next_question_id": "q4_solo",
            },
        ],
    },

    "q3_excited": {
        "id": "q3_excited",
        "text": "What kind of excitement are you feeling?",
        "options": [
            {
                "text": "Pumped up — adrenaline rush!",
                "mood_scores": {"excited": 0.7},
                "next_question_id": "q4_intense",
            },
            {
                "text": "Warm and joyful — life is good",
                "mood_scores": {"happy": 0.5, "excited": 0.3},
                "next_question_id": "q4_social",
            },
        ],
    },

    "q3_neutral": {
        "id": "q3_neutral",
        "text": "What sounds most appealing right now?",
        "options": [
            {
                "text": "Discovering something new and interesting",
                "mood_scores": {"neutral": 0.3, "excited": 0.3},
                "next_question_id": "q4_solo",
            },
            {
                "text": "Just unwinding and de-stressing",
                "mood_scores": {"stressed": 0.3, "neutral": 0.4},
                "next_question_id": "q4_solo",
            },
        ],
    },

    "q3_stressed": {
        "id": "q3_stressed",
        "text": "How would you like to cope right now?",
        "options": [
            {
                "text": "Active distraction — keep me busy",
                "mood_scores": {"stressed": 0.3, "excited": 0.3},
                "next_question_id": "q4_intense",
            },
            {
                "text": "Gentle relaxation — help me wind down",
                "mood_scores": {"stressed": 0.5, "neutral": 0.2},
                "next_question_id": "q4_solo",
            },
        ],
    },

    # ── Level 4 (final) Questions ────────────────────────────────────
    "q4_social": {
        "id": "q4_social",
        "text": "Pick the vibe that appeals to you most:",
        "options": [
            {
                "text": "🎉 Party & celebration",
                "mood_scores": {"excited": 0.5, "happy": 0.4},
                "next_question_id": None,
            },
            {
                "text": "😊 Feel-good & heartwarming",
                "mood_scores": {"happy": 0.7},
                "next_question_id": None,
            },
            {
                "text": "🤝 Meaningful & thought-provoking",
                "mood_scores": {"neutral": 0.4, "sad": 0.2},
                "next_question_id": None,
            },
        ],
    },

    "q4_solo": {
        "id": "q4_solo",
        "text": "What atmosphere do you prefer?",
        "options": [
            {
                "text": "🌙 Quiet and contemplative",
                "mood_scores": {"neutral": 0.4, "sad": 0.2},
                "next_question_id": None,
            },
            {
                "text": "🌿 Peaceful and healing",
                "mood_scores": {"stressed": 0.4, "neutral": 0.3},
                "next_question_id": None,
            },
            {
                "text": "🌅 Inspiring and uplifting",
                "mood_scores": {"happy": 0.4, "excited": 0.2},
                "next_question_id": None,
            },
        ],
    },

    "q4_intense": {
        "id": "q4_intense",
        "text": "What intensity level do you want?",
        "options": [
            {
                "text": "🔥 Maximum intensity — blow off steam",
                "mood_scores": {"angry": 0.3, "excited": 0.5},
                "next_question_id": None,
            },
            {
                "text": "⚡ High energy but fun",
                "mood_scores": {"excited": 0.6, "happy": 0.2},
                "next_question_id": None,
            },
            {
                "text": "💪 Motivational and empowering",
                "mood_scores": {"excited": 0.4, "happy": 0.3},
                "next_question_id": None,
            },
        ],
    },
}


def get_first_question():
    """Return the first question in the tree."""
    return QUESTIONS["q1"]


def get_question(question_id):
    """Return a question by its ID, or None if not found."""
    return QUESTIONS.get(question_id)


def get_all_question_ids():
    """Return all question IDs (useful for debugging)."""
    return list(QUESTIONS.keys())
