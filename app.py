"""
Mood-Based Song & Movie Recommendation System
Flask Web Application — Main Entry Point
"""

import os
import sys
import json
import base64
import tempfile

from flask import (
    Flask, render_template, request, jsonify, session, redirect, url_for
)

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_utils import init_db
from database.seed_data import seed_database
from emotion.predict import predict_emotion, predict_emotion_from_bytes
from questionnaire.questions import get_first_question, get_question
from questionnaire.scorer import score_responses
from fusion.mood_fusion import fuse_moods
from recommender.engine import get_recommendations

# ── Flask App Setup ──────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = "mood-recommendation-secret-key-2024"

# Upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ── Initialize Database on Startup ──────────────────────────────────────
with app.app_context():
    seed_database()


# ── Routes ──────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Landing page."""
    # Clear any previous session data
    session.pop("cnn_result", None)
    session.pop("quest_responses", None)
    session.pop("quest_result", None)
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_image():
    """Handle image upload or webcam capture for emotion detection."""
    try:
        cnn_result = None

        # Check if it's a webcam capture (base64 data)
        if request.is_json:
            data = request.get_json()
            image_data = data.get("image", "")

            # Remove data URL prefix if present
            if "," in image_data:
                image_data = image_data.split(",")[1]

            image_bytes = base64.b64decode(image_data)
            cnn_result = predict_emotion_from_bytes(image_bytes)

        # Check if it's a file upload
        elif "image" in request.files:
            file = request.files["image"]
            if file.filename == "":
                return jsonify({"error": "No file selected"}), 400

            # Save temporarily
            filepath = os.path.join(UPLOAD_FOLDER, "temp_upload.jpg")
            file.save(filepath)
            cnn_result = predict_emotion(filepath)

            # Clean up
            try:
                os.remove(filepath)
            except OSError:
                pass
        else:
            return jsonify({"error": "No image provided"}), 400

        if not cnn_result["face_found"]:
            return jsonify({
                "error": "No face detected in the image. Please try again with a clearer photo.",
                "face_found": False,
            }), 200

        # Store CNN result in session
        session["cnn_result"] = cnn_result

        return jsonify({
            "face_found": True,
            "emotion": cnn_result["emotion"],
            "mood": cnn_result["mood"],
            "confidence": round(cnn_result["confidence"] * 100, 1),
            "mood_scores": {k: round(v, 4) for k, v in cnn_result["mood_scores"].items()},
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/questionnaire", methods=["GET"])
def questionnaire_page():
    """Serve the questionnaire page."""
    return render_template("questionnaire.html")


@app.route("/api/question/<question_id>", methods=["GET"])
def get_question_api(question_id):
    """API to get a specific question by ID."""
    question = get_question(question_id)
    if question is None:
        return jsonify({"error": "Question not found"}), 404
    return jsonify(question)


@app.route("/api/first-question", methods=["GET"])
def first_question_api():
    """API to get the first question."""
    question = get_first_question()
    return jsonify(question)


@app.route("/api/submit-questionnaire", methods=["POST"])
def submit_questionnaire():
    """Process completed questionnaire responses."""
    try:
        data = request.get_json()
        responses = data.get("responses", [])

        if not responses:
            return jsonify({"error": "No responses provided"}), 400

        # Score the responses
        quest_result = score_responses(responses)

        # Store in session
        session["quest_result"] = quest_result

        return jsonify({
            "top_mood": quest_result["top_mood"],
            "mood_scores": {k: round(v, 4) for k, v in quest_result["mood_scores"].items()},
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/results")
def results():
    """Show final mood and recommendations."""
    # Retrieve session data
    cnn_result = session.get("cnn_result")
    quest_result = session.get("quest_result")

    # Get mood scores from each source
    cnn_mood_scores = cnn_result.get("mood_scores") if cnn_result else None
    quest_mood_scores = quest_result.get("mood_scores") if quest_result else None

    # Fuse moods
    fusion = fuse_moods(
        cnn_mood_scores=cnn_mood_scores,
        questionnaire_mood_scores=quest_mood_scores,
    )

    # Get recommendations
    recs = get_recommendations(
        final_mood=fusion["final_mood"],
        cnn_emotion=cnn_result.get("emotion") if cnn_result else None,
        cnn_confidence=cnn_result.get("confidence") if cnn_result else None,
        questionnaire_mood=quest_result.get("top_mood") if quest_result else None,
        questionnaire_score=max(quest_result["mood_scores"].values()) if quest_result else None,
    )

    # Mood emoji mapping
    mood_emojis = {
        "happy": "😊",
        "sad": "😢",
        "angry": "😠",
        "neutral": "😐",
        "excited": "🤩",
        "stressed": "😰",
    }

    return render_template(
        "results.html",
        mood=fusion["final_mood"],
        mood_emoji=mood_emojis.get(fusion["final_mood"], "🎭"),
        confidence=round(fusion["confidence"] * 100, 1),
        scores=fusion["final_scores"],
        songs=recs["songs"],
        movies=recs["movies"],
        cnn_used=fusion["cnn_used"],
        quest_used=fusion["quest_used"],
        cnn_emotion=cnn_result.get("emotion") if cnn_result else None,
        quest_mood=quest_result.get("top_mood") if quest_result else None,
    )


@app.route("/api/skip-image", methods=["POST"])
def skip_image():
    """Skip the image analysis step."""
    session.pop("cnn_result", None)
    return jsonify({"status": "ok"})


@app.route("/api/skip-questionnaire", methods=["POST"])
def skip_questionnaire():
    """Skip the questionnaire step."""
    session.pop("quest_result", None)
    return jsonify({"status": "ok"})


# ── Main ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n🎭 Mood-Based Recommendation System")
    print("   Open http://localhost:5000 in your browser\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
