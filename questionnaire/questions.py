"""
Dynamic Questionnaire Module — v2 (Situational / Behavioral)
Adaptive question tree with 7 mood categories.

Questions use behavioral proxies — everyday scenarios that indirectly
reveal the user's subconscious emotional state more accurately than
direct "how do you feel?" questions.

Supported moods: happy, sad, angry, neutral, excited, stressed, calm
"""

import random

MOOD_CATEGORIES = [
    "happy", "sad", "angry", "neutral", "excited", "stressed", "calm",
]

# ── Question Pool (multiple variants per slot for dynamism) ──────

# Level 1 — Gateway question (random from pool)
Q1_POOL = [
    {
        "id": "q1",
        "text": "It's a free evening with no plans. What do you instinctively reach for?",
        "options": [
            {
                "text": "🎊 Call friends — let's do something fun!",
                "mood_scores": {"excited": 0.5, "happy": 0.5},
                "next_question_id": "q2_high_energy",
            },
            {
                "text": "☕ A warm drink and a quiet corner",
                "mood_scores": {"calm": 0.5, "neutral": 0.3, "sad": 0.2},
                "next_question_id": "q2_moderate",
            },
            {
                "text": "🛌 Honestly, I'd just lie down and zone out",
                "mood_scores": {"sad": 0.5, "stressed": 0.3, "calm": 0.2},
                "next_question_id": "q2_low_energy",
            },
            {
                "text": "🥊 I need to blow off some steam",
                "mood_scores": {"angry": 0.5, "stressed": 0.4, "excited": 0.1},
                "next_question_id": "q2_agitated",
            },
        ],
    },
    {
        "id": "q1",
        "text": "You receive an unexpected message from an old friend. Your first reaction?",
        "options": [
            {
                "text": "😄 Instant smile — I'm calling them right now!",
                "mood_scores": {"happy": 0.5, "excited": 0.5},
                "next_question_id": "q2_high_energy",
            },
            {
                "text": "🤔 Hmm, interesting — I'll reply later when I feel like it",
                "mood_scores": {"neutral": 0.5, "calm": 0.3, "happy": 0.2},
                "next_question_id": "q2_moderate",
            },
            {
                "text": "😔 It makes me nostalgic and a bit emotional",
                "mood_scores": {"sad": 0.6, "calm": 0.4},
                "next_question_id": "q2_low_energy",
            },
            {
                "text": "😒 Not in the mood to deal with people right now",
                "mood_scores": {"angry": 0.3, "stressed": 0.5, "neutral": 0.2},
                "next_question_id": "q2_agitated",
            },
        ],
    },
    {
        "id": "q1",
        "text": "A song starts playing randomly. Which kind would match your current vibe?",
        "options": [
            {
                "text": "🔥 Something with a sick beat — I need energy!",
                "mood_scores": {"excited": 0.5, "happy": 0.5},
                "next_question_id": "q2_high_energy",
            },
            {
                "text": "🎶 Soft melody, something easy to hum along to",
                "mood_scores": {"calm": 0.5, "neutral": 0.3, "happy": 0.2},
                "next_question_id": "q2_moderate",
            },
            {
                "text": "🎻 Something that understands my feelings right now",
                "mood_scores": {"sad": 0.6, "stressed": 0.2, "calm": 0.2},
                "next_question_id": "q2_low_energy",
            },
            {
                "text": "🎸 Heavy, intense — match my frustration",
                "mood_scores": {"angry": 0.5, "stressed": 0.3, "excited": 0.2},
                "next_question_id": "q2_agitated",
            },
        ],
    },
]


QUESTIONS = {
    # ── Level 2 ─────────────────────────────────────────

    "q2_high_energy": {
        "id": "q2_high_energy",
        "text": "You just got some great news. What's your next move?",
        "options": [
            {
                "text": "🎉 Celebrate! Party mode: ON",
                "mood_scores": {"excited": 0.6, "happy": 0.4},
                "next_question_id": "q3_excited",
            },
            {
                "text": "😊 I'm just savoring the moment quietly with a big smile",
                "mood_scores": {"happy": 0.7, "calm": 0.3},
                "next_question_id": "q3_happy",
            },
            {
                "text": "💪 This motivates me to chase something even bigger",
                "mood_scores": {"excited": 0.5, "happy": 0.5},
                "next_question_id": "q3_happy",
            },
            {
                "text": "😰 I'm excited but also nervous — there's so much to do",
                "mood_scores": {"stressed": 0.5, "excited": 0.5},
                "next_question_id": "q3_stressed",
            },
        ],
    },

    "q2_moderate": {
        "id": "q2_moderate",
        "text": "If you could teleport anywhere right now, where would you go?",
        "options": [
            {
                "text": "🏖️ A beach sunset — peaceful and beautiful",
                "mood_scores": {"calm": 0.6, "happy": 0.4},
                "next_question_id": "q3_calm",
            },
            {
                "text": "🏔️ A quiet mountaintop, just me and nature",
                "mood_scores": {"calm": 0.6, "neutral": 0.4},
                "next_question_id": "q3_calm",
            },
            {
                "text": "🎢 An amusement park — I want thrills!",
                "mood_scores": {"excited": 0.5, "happy": 0.5},
                "next_question_id": "q3_happy",
            },
            {
                "text": "🌧️ A rainy café with a journal and deep thoughts",
                "mood_scores": {"sad": 0.4, "calm": 0.3, "neutral": 0.3},
                "next_question_id": "q3_sad",
            },
        ],
    },

    "q2_low_energy": {
        "id": "q2_low_energy",
        "text": "What would comfort you most right now?",
        "options": [
            {
                "text": "🍫 Comfort food and a nostalgic movie — just let me feel it",
                "mood_scores": {"sad": 0.6, "calm": 0.4},
                "next_question_id": "q3_sad",
            },
            {
                "text": "🧘 Deep breaths and some silence — I need to reset",
                "mood_scores": {"calm": 0.5, "stressed": 0.3, "neutral": 0.2},
                "next_question_id": "q3_calm",
            },
            {
                "text": "💬 Talking to someone who truly gets me",
                "mood_scores": {"sad": 0.4, "happy": 0.3, "calm": 0.3},
                "next_question_id": "q3_sad",
            },
            {
                "text": "🎧 Something uplifting to pull me out of this",
                "mood_scores": {"happy": 0.5, "excited": 0.5},
                "next_question_id": "q3_happy",
            },
        ],
    },

    "q2_agitated": {
        "id": "q2_agitated",
        "text": "Someone cuts you off in traffic. How do you respond?",
        "options": [
            {
                "text": "🤬 I honk and vent — are they serious?!",
                "mood_scores": {"angry": 0.7, "stressed": 0.3},
                "next_question_id": "q3_angry",
            },
            {
                "text": "😤 I clench the steering wheel but stay quiet",
                "mood_scores": {"stressed": 0.6, "angry": 0.4},
                "next_question_id": "q3_stressed",
            },
            {
                "text": "😒 Whatever. I'm too tired to even care",
                "mood_scores": {"neutral": 0.4, "sad": 0.3, "calm": 0.3},
                "next_question_id": "q3_calm",
            },
            {
                "text": "💪 I channel the frustration — gonna use this energy",
                "mood_scores": {"excited": 0.5, "angry": 0.3, "happy": 0.2},
                "next_question_id": "q3_excited",
            },
        ],
    },

    # ── Level 3 ─────────────────────────────────────────

    "q3_happy": {
        "id": "q3_happy",
        "text": "You're at a party. What are you doing?",
        "options": [
            {
                "text": "💃 Dancing like nobody's watching!",
                "mood_scores": {"happy": 0.5, "excited": 0.5},
                "next_question_id": "q4_social",
            },
            {
                "text": "😌 Chatting with close friends in a cozy corner",
                "mood_scores": {"happy": 0.6, "calm": 0.4},
                "next_question_id": "q4_solo",
            },
        ],
    },

    "q3_sad": {
        "id": "q3_sad",
        "text": "When you're feeling low, which of these helps more?",
        "options": [
            {
                "text": "🌤️ Something that makes me laugh and forget",
                "mood_scores": {"happy": 0.6, "excited": 0.4},
                "next_question_id": "q4_social",
            },
            {
                "text": "🌊 Something beautiful and melancholic that validates my feelings",
                "mood_scores": {"sad": 0.7, "calm": 0.3},
                "next_question_id": "q4_solo",
            },
        ],
    },

    "q3_angry": {
        "id": "q3_angry",
        "text": "You need to release tension. What sounds right?",
        "options": [
            {
                "text": "🥁 Something loud, fast, and aggressive",
                "mood_scores": {"angry": 0.5, "excited": 0.5},
                "next_question_id": "q4_intense",
            },
            {
                "text": "🌿 Actually, something calming to bring me back to earth",
                "mood_scores": {"calm": 0.6, "neutral": 0.4},
                "next_question_id": "q4_solo",
            },
        ],
    },

    "q3_excited": {
        "id": "q3_excited",
        "text": "What kind of excitement are you feeling?",
        "options": [
            {
                "text": "⚡ Pure adrenaline — I want edge-of-seat stuff!",
                "mood_scores": {"excited": 0.7, "happy": 0.3},
                "next_question_id": "q4_intense",
            },
            {
                "text": "☀️ Warm, buzzy joy — life is genuinely good right now",
                "mood_scores": {"happy": 0.6, "excited": 0.4},
                "next_question_id": "q4_social",
            },
        ],
    },

    "q3_calm": {
        "id": "q3_calm",
        "text": "You have the whole afternoon to yourself. What do you choose?",
        "options": [
            {
                "text": "📖 A cozy blanket and a gentle story — pure serenity",
                "mood_scores": {"calm": 0.7, "happy": 0.3},
                "next_question_id": "q4_solo",
            },
            {
                "text": "🫖 Just breathe. Meditate. Let it all go.",
                "mood_scores": {"calm": 0.6, "neutral": 0.4},
                "next_question_id": "q4_solo",
            },
        ],
    },

    "q3_stressed": {
        "id": "q3_stressed",
        "text": "Your to-do list is overflowing. How do you cope?",
        "options": [
            {
                "text": "🏃 Active distraction — gym, run, something physical",
                "mood_scores": {"excited": 0.4, "stressed": 0.3, "happy": 0.3},
                "next_question_id": "q4_intense",
            },
            {
                "text": "🛀 Full shutdown mode — bath, candles, don't talk to me",
                "mood_scores": {"calm": 0.5, "stressed": 0.3, "sad": 0.2},
                "next_question_id": "q4_solo",
            },
        ],
    },

    "q3_neutral": {
        "id": "q3_neutral",
        "text": "What sounds most appealing right now?",
        "options": [
            {
                "text": "🔍 Discovering something new and interesting",
                "mood_scores": {"neutral": 0.3, "excited": 0.4, "happy": 0.3},
                "next_question_id": "q4_solo",
            },
            {
                "text": "🌅 Just vibing, no agenda needed",
                "mood_scores": {"calm": 0.5, "neutral": 0.5},
                "next_question_id": "q4_solo",
            },
        ],
    },

    # ── Level 4 (Final) ─────────────────────────────────

    "q4_social": {
        "id": "q4_social",
        "text": "One last thing — pick the word that resonates most:",
        "options": [
            {"text": "🎉 Celebration", "mood_scores": {"excited": 0.5, "happy": 0.5}, "next_question_id": None},
            {"text": "🌤️ Warmth", "mood_scores": {"happy": 0.6, "calm": 0.4}, "next_question_id": None},
            {"text": "🚀 Ambition", "mood_scores": {"excited": 0.6, "happy": 0.4}, "next_question_id": None},
            {"text": "🧩 Curiosity", "mood_scores": {"neutral": 0.5, "calm": 0.3, "happy": 0.2}, "next_question_id": None},
        ],
    },

    "q4_solo": {
        "id": "q4_solo",
        "text": "Last question — which atmosphere calls to you?",
        "options": [
            {"text": "🌙 Quiet moonlit night", "mood_scores": {"calm": 0.5, "neutral": 0.3, "sad": 0.2}, "next_question_id": None},
            {"text": "🌿 Sunlit forest — fresh and healing", "mood_scores": {"calm": 0.6, "happy": 0.4}, "next_question_id": None},
            {"text": "🌅 Golden sunrise — new beginnings", "mood_scores": {"happy": 0.5, "excited": 0.3, "calm": 0.2}, "next_question_id": None},
            {"text": "🌊 Ocean waves — rhythm that grounds me", "mood_scores": {"calm": 0.6, "neutral": 0.4}, "next_question_id": None},
        ],
    },

    "q4_intense": {
        "id": "q4_intense",
        "text": "Final pick — what intensity level do you want?",
        "options": [
            {"text": "🔥 Maximum — let me feel ALIVE", "mood_scores": {"angry": 0.3, "excited": 0.7}, "next_question_id": None},
            {"text": "⚡ High energy but fun and upbeat", "mood_scores": {"excited": 0.5, "happy": 0.5}, "next_question_id": None},
            {"text": "💪 Powerful and empowering", "mood_scores": {"excited": 0.5, "happy": 0.5}, "next_question_id": None},
        ],
    },
}


def get_first_question():
    """Return a randomly selected Level 1 question for dynamism."""
    return random.choice(Q1_POOL)

def get_question(question_id):
    """Get question by ID. For q1, return from pool randomly."""
    if question_id == "q1":
        return random.choice(Q1_POOL)
    return QUESTIONS.get(question_id)

def get_all_question_ids():
    return ["q1"] + list(QUESTIONS.keys())
