# Mood Fusion: 50% CNN + 50% Questionnaire (equal weight)
# final_score = (cnn_score * 0.5) + (question_score * 0.5)


import os, sys, json, base64, tempfile, functools
from flask import (
    Flask, render_template, request, jsonify, session, redirect, url_for, flash
)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_utils import (
    init_db, create_user, verify_user, get_user_by_id, get_user_mood_history
)
from database.seed_data import seed_database
from emotion.predict import predict_emotion, predict_emotion_from_bytes
from questionnaire.questions import get_first_question, get_question
from questionnaire.scorer import score_responses
from fusion.mood_fusion import fuse_moods
from recommender.engine import get_recommendations

app = Flask(__name__)
app.secret_key = "mood-recommendation-secret-key-2024"

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

with app.app_context():
    seed_database()


def login_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def get_current_user():
    uid = session.get("user_id")
    if uid:
        return get_user_by_id(uid)
    return None


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html")
        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")
        if len(password) < 4:
            flash("Password must be at least 4 characters.", "danger")
            return render_template("register.html")

        user = create_user(username, email, password)
        if not user:
            flash("Username or email already exists.", "danger")
            return render_template("register.html")

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        flash(f"Welcome, {user['username']}! 🎉", "success")
        return redirect(url_for("index"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = verify_user(username, password)
        if not user:
            flash("Invalid username or password.", "danger")
            return render_template("login.html")

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        flash(f"Welcome back, {user['username']}! 👋", "success")
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/profile")
@login_required
def profile():
    user = get_current_user()
    raw_history = get_user_mood_history(session["user_id"], limit=15)

    mood_emojis = {
        "happy": "😊", "sad": "😢", "angry": "😠", "neutral": "😐",
        "excited": "🤩", "stressed": "😰", "calm": "🧘",
    }

    # Enrich history entries with derived display fields
    mood_history = []
    mood_counts = {}
    from datetime import datetime
    current_month = datetime.now().strftime("%Y-%m")
    this_month_count = 0

    for entry in raw_history:
        e = dict(entry)
        e["mood"] = e.get("final_mood", "neutral")
        e["emoji"] = mood_emojis.get(e["mood"], "🎭")
        e["cnn_used"] = bool(e.get("cnn_emotion"))
        e["quest_used"] = bool(e.get("questionnaire_mood"))
        e["confidence"] = round((e.get("cnn_confidence") or 0) * 100, 1) if e.get("cnn_confidence") else "—"
        mood_history.append(e)
        mood_counts[e["mood"]] = mood_counts.get(e["mood"], 0) + 1
        if e.get("timestamp", "").startswith(current_month):
            this_month_count += 1

    top_mood = max(mood_counts, key=mood_counts.get) if mood_counts else None
    stats = {
        "total_sessions": len(raw_history),
        "top_mood": top_mood,
        "this_month": this_month_count,
    }

    return render_template("profile.html", user=user, mood_history=mood_history, stats=stats)


@app.route("/")
@login_required
def index():
    session.pop("cnn_result", None)
    session.pop("quest_responses", None)
    session.pop("quest_result", None)
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
@login_required
def upload_image():
    try:
        cnn_result = None
        if request.is_json:
            data = request.get_json()
            image_data = data.get("image", "")
            if "," in image_data:
                image_data = image_data.split(",")[1]
            image_bytes = base64.b64decode(image_data)
            cnn_result = predict_emotion_from_bytes(image_bytes)
        elif "image" in request.files:
            file = request.files["image"]
            if file.filename == "":
                return jsonify({"error": "No file selected"}), 400
            filepath = os.path.join(UPLOAD_FOLDER, "temp_upload.jpg")
            file.save(filepath)
            cnn_result = predict_emotion(filepath)
            try:
                os.remove(filepath)
            except OSError:
                pass
        else:
            return jsonify({"error": "No image provided"}), 400

        if not cnn_result["face_found"]:
            return jsonify({"error": "No face detected.", "face_found": False}), 200

        # Preview mode: return results without saving to session (live webcam)
        is_preview = request.is_json and request.get_json().get("preview", False)
        if not is_preview:
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


@app.route("/questionnaire")
@login_required
def questionnaire_page():
    return render_template("questionnaire.html")


@app.route("/api/question/<question_id>")
def get_question_api(question_id):
    question = get_question(question_id)
    if question is None:
        return jsonify({"error": "Question not found"}), 404
    return jsonify(question)


@app.route("/api/first-question")
def first_question_api():
    return jsonify(get_first_question())


@app.route("/api/submit-questionnaire", methods=["POST"])
@login_required
def submit_questionnaire():
    try:
        data = request.get_json()
        responses = data.get("responses", [])
        if not responses:
            return jsonify({"error": "No responses provided"}), 400
        quest_result = score_responses(responses)
        session["quest_result"] = quest_result
        return jsonify({
            "top_mood": quest_result["top_mood"],
            "mood_scores": {k: round(v, 4) for k, v in quest_result["mood_scores"].items()},
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/results")
@login_required
def results():
    cnn_result = session.get("cnn_result")
    quest_result = session.get("quest_result")

    cnn_mood_scores = cnn_result.get("mood_scores") if cnn_result else None
    quest_mood_scores = quest_result.get("mood_scores") if quest_result else None

    fusion = fuse_moods(cnn_mood_scores=cnn_mood_scores, questionnaire_mood_scores=quest_mood_scores)

    recs = get_recommendations(
        final_mood=fusion["final_mood"],
        user_id=session.get("user_id"),
        cnn_emotion=cnn_result.get("emotion") if cnn_result else None,
        cnn_confidence=cnn_result.get("confidence") if cnn_result else None,
        questionnaire_mood=quest_result.get("top_mood") if quest_result else None,
        questionnaire_score=max(quest_result["mood_scores"].values()) if quest_result else None,
    )

    mood_emojis = {
        "happy": "😊", "sad": "😢", "angry": "😠", "neutral": "😐",
        "excited": "🤩", "stressed": "😰", "calm": "🧘",
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
@login_required
def skip_image():
    session.pop("cnn_result", None)
    return jsonify({"status": "ok"})


@app.route("/api/skip-questionnaire", methods=["POST"])
@login_required
def skip_questionnaire():
    session.pop("quest_result", None)
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    print("\n🎭 Mood-Based Recommendation System")
    print("   Open http://localhost:5001 in your browser\n")
    app.run(debug=True, host="0.0.0.0", port=5001)
