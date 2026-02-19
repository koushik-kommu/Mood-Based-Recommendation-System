# 🎭 MoodSync — Mood-Based Song & Movie Recommendation System

A machine learning-powered web application that detects your emotional state through **facial expression analysis (CNN)** and a **dynamic questionnaire**, then recommends mood-matched **songs** and **movies** with working links.

---

## 📋 Table of Contents

- [Features](#-features)
- [Project Architecture](#-project-architecture)
- [Steps to Execute the Project](#-steps-to-execute-the-project)
- [Project Lifecycle (Start to Termination)](#-project-lifecycle-start-to-termination)
- [Tech Stack](#-tech-stack)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎯 Facial Emotion Recognition | CNN trained on FER-2013 dataset (59.9% accuracy) |
| 📝 Dynamic Questionnaire | Adaptive branching questions that change based on answers |
| 🔀 Mood Fusion Engine | Weighted combination (60% CNN + 40% Questionnaire) |
| 🎵 Song Recommendations | 60 songs across 6 moods with YouTube links |
| 🎬 Movie Recommendations | 60 movies across 6 moods with OTT platform links |
| 🌙 Modern Dark UI | Glassmorphism, particle animations, responsive design |

**Supported Moods:** Happy, Sad, Angry, Neutral, Excited, Stressed

---

## 🏗 Project Architecture

```
mood/
├── app.py                     # Flask application (main entry point)
├── requirements.txt           # Python dependencies
├── database/
│   ├── schema.sql             # SQLite schema (songs, movies, mood_history)
│   ├── db_utils.py            # DB connection & query helpers
│   └── seed_data.py           # Seed data (60 songs + 60 movies)
├── emotion/
│   ├── face_detector.py       # Haar Cascade face detection + preprocessing
│   ├── emotion_model.py       # CNN architecture (3 conv blocks)
│   ├── train_model.py         # Model training script
│   ├── predict.py             # Prediction API
│   └── emotion_model.h5       # Trained model weights (generated after training)
├── questionnaire/
│   ├── questions.py           # Adaptive question tree (13 nodes)
│   └── scorer.py              # Response scoring & normalization
├── fusion/
│   └── mood_fusion.py         # Weighted mood fusion logic
├── recommender/
│   └── engine.py              # Content-based recommendation engine
├── templates/
│   ├── base.html              # Base layout (dark theme)
│   ├── index.html             # Step 1: Image upload / webcam
│   ├── questionnaire.html     # Step 2: Adaptive questionnaire
│   └── results.html           # Step 3: Mood & recommendations
├── static/
│   ├── css/style.css          # Glassmorphism dark theme
│   └── js/main.js             # Particle animations
└── tests/
    └── __init__.py
```

---

## 🚀 Steps to Execute the Project

### Step 1: Clone the Repository
```bash
git clone https://github.com/koushik-kommu/Mood-Based-Recommendation-System.git
cd Mood-Based-Recommendation-System
```

### Step 2: Install Dependencies
```bash
pip3 install -r requirements.txt
pip3 install scipy kagglehub  # Additional dependencies for CNN training
```

### Step 3: Train the CNN Model (One-Time Setup)
```bash
python3 -m emotion.train_model
```
> This automatically downloads the FER-2013 dataset (~60 MB) from Kaggle and trains the CNN.  
> Training takes ~15 minutes and saves the model to `emotion/emotion_model.h5`.  
> **Note:** The app works without this step using the questionnaire-only path.

### Step 4: Run the Application
```bash
python3 app.py
```
The database is automatically initialized and seeded on first run.

### Step 5: Open in Browser
```
http://localhost:5000
```

### Step 6: Use the Application
1. **Upload a photo** or **use your webcam** for facial emotion detection
2. **Answer 4 adaptive questions** in the dynamic questionnaire
3. **View your detected mood** and get personalized song & movie recommendations

### Step 7: Stop the Server
Press `Ctrl + C` in the terminal to stop Flask.

---

## 🔄 Project Lifecycle (Start to Termination)

### Phase 1 — Initialization (Automatic on First Run)
```
python3 app.py
```
When the app starts for the first time:
1. **Database Creation** → SQLite DB is created at `database/mood_recommendations.db`
2. **Schema Setup** → Tables `songs`, `movies`, `mood_history` are created from `schema.sql`
3. **Data Seeding** → 60 songs and 60 movies are inserted across 6 mood categories
4. **Flask Server** → Starts on `http://0.0.0.0:5000` in debug mode

### Phase 2 — User Input (Step 1: Face Analysis)
```
Route: GET /  →  POST /upload  or  POST /api/capture
```
1. User opens the landing page at `/`
2. **Option A — Upload Photo:** User selects an image file → sent to `/upload`
3. **Option B — Webcam Capture:** Browser captures a frame → sent to `/api/capture`
4. **Option C — Skip:** User clicks "Skip this step" → sent to `/api/skip-image`

**Processing (if image provided):**
- Haar Cascade detects faces in the image
- Face is cropped, converted to grayscale, resized to 48×48
- CNN predicts emotion probabilities across 7 FER classes
- Probabilities are mapped to 6 project moods and stored in session

### Phase 3 — User Input (Step 2: Questionnaire)
```
Route: GET /questionnaire  →  GET /api/first-question  →  GET /api/question/<id>
```
1. First question is loaded via `/api/first-question`
2. User selects an answer → triggers loading the next branching question
3. Questions adapt dynamically based on previous answers (13 possible paths)
4. After 4 questions, responses are submitted to `/api/submit-questionnaire`

**Processing:**
- Each answer carries mood scores (e.g., `{Happy: 0.3, Excited: 0.7}`)
- Scores are aggregated and normalized to sum to 1.0
- Result is stored in session

### Phase 4 — Mood Fusion & Recommendation (Step 3: Results)
```
Route: GET /results
```
**Fusion Logic:**
- If both inputs available: `Final = 0.6 × CNN + 0.4 × Questionnaire`
- If only one input: uses that input at 100%
- Dominant mood (highest score) is selected

**Recommendation:**
- SQLite is queried for songs and movies matching the dominant mood
- 5 random songs with YouTube links are returned
- 5 random movies with OTT platform links are returned
- Results are logged to `mood_history` table

**Display:**
- Mood emoji, label, and confidence percentage
- Source badges (CNN / Questionnaire)
- Animated mood breakdown bar chart
- Song and movie recommendation cards with clickable links

### Phase 5 — Repeat or Terminate
- **Try Again:** User clicks "Try Again" → redirects to `/` (Phase 2)
- **History:** Each session is logged in `mood_history` for tracking
- **Terminate:** Press `Ctrl + C` in terminal to stop the Flask server

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask |
| ML Model | TensorFlow/Keras CNN (FER-2013) |
| Face Detection | OpenCV Haar Cascade |
| Database | SQLite |
| Frontend | HTML5, CSS3 (Glassmorphism), Vanilla JS |
| Dataset | FER-2013 (28,709 images, 7 emotions) |

---

## 👤 Author

**Kommu Koushik**

---
