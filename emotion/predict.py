"""
Emotion Prediction API
Public interface for the facial emotion recognition pipeline.
"""

import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from emotion.face_detector import detect_face, detect_face_from_bytes
from emotion.emotion_model import (
    get_model,
    EMOTION_LABELS,
    EMOTION_TO_MOOD,
    emotion_to_mood_scores,
)


# Module-level model cache
_model = None


def _get_cached_model():
    """Load model once and cache it."""
    global _model
    if _model is None:
        _model = get_model()
    return _model


def predict_emotion(image_path):
    """
    Predict emotion from an image file.

    Parameters
    ----------
    image_path : str
        Path to an image file containing a face.

    Returns
    -------
    dict with keys:
        emotion    : str   — Predicted FER emotion label
        mood       : str   — Mapped mood category
        confidence : float — Confidence of the top prediction
        mood_scores: dict  — Scores for all 6 mood categories
        face_found : bool  — Whether a face was detected
    """
    face_roi, original, face_coords = detect_face(image_path)

    if face_roi is None:
        return {
            "emotion": None,
            "mood": None,
            "confidence": 0.0,
            "mood_scores": {},
            "face_found": False,
        }

    return _classify(face_roi)


def predict_emotion_from_bytes(image_bytes):
    """
    Predict emotion from raw image bytes (webcam capture).

    Parameters
    ----------
    image_bytes : bytes
        Raw image data (JPEG/PNG).

    Returns
    -------
    dict — Same structure as predict_emotion().
    """
    face_roi, original, face_coords = detect_face_from_bytes(image_bytes)

    if face_roi is None:
        return {
            "emotion": None,
            "mood": None,
            "confidence": 0.0,
            "mood_scores": {},
            "face_found": False,
        }

    return _classify(face_roi)


def _classify(face_roi):
    """
    Run the CNN on a preprocessed 48x48 face patch.

    Parameters
    ----------
    face_roi : np.ndarray
        Shape (48, 48), values in [0, 1].

    Returns
    -------
    dict
    """
    model = _get_cached_model()

    # Reshape for model input: (1, 48, 48, 1)
    face_input = face_roi.reshape(1, 48, 48, 1)

    # Predict
    probabilities = model.predict(face_input, verbose=0)[0]

    # Top emotion
    top_idx = int(np.argmax(probabilities))
    emotion = EMOTION_LABELS[top_idx]
    confidence = float(probabilities[top_idx])
    mood = EMOTION_TO_MOOD[emotion]

    # Mood scores
    mood_scores = emotion_to_mood_scores(probabilities)

    return {
        "emotion": emotion,
        "mood": mood,
        "confidence": confidence,
        "mood_scores": mood_scores,
        "face_found": True,
    }
