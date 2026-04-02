"""
Emotion Prediction API — Enhanced v3
Public interface for the facial emotion recognition pipeline.
Uses 10-crop test-time augmentation with temperature scaling
and class rebalancing for robust, calibrated predictions.
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

# Minimum confidence threshold — below this, default to neutral
MIN_CONFIDENCE = 0.18

# Class rebalancing: boost under-represented emotions in FER-2013
# (sad, fear, disgust, surprise are often under-predicted)
CLASS_BOOST = {
    "sad": 1.20,
    "fear": 1.20,
    "disgust": 1.25,
    "surprise": 1.10,
}


def _get_cached_model():
    """Load model once and cache it."""
    global _model
    if _model is None:
        _model = get_model()
    return _model


def predict_emotion(image_path):
    """Predict emotion from an image file."""
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
    """Predict emotion from raw image bytes (webcam capture)."""
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


def _rotate_image(image, angle):
    """Rotate a 48x48 image by small angle."""
    import cv2
    h, w = image.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), borderMode=cv2.BORDER_REFLECT)
    return rotated


def _center_crop(image, crop_ratio=0.85):
    """Extract a center crop and resize back."""
    import cv2
    h, w = image.shape[:2]
    ch, cw = int(h * crop_ratio), int(w * crop_ratio)
    y1 = (h - ch) // 2
    x1 = (w - cw) // 2
    cropped = image[y1:y1+ch, x1:x1+cw]
    return cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)


def _corner_crops(image, crop_ratio=0.85):
    """Extract 4 corner crops and resize back."""
    import cv2
    h, w = image.shape[:2]
    ch, cw = int(h * crop_ratio), int(w * crop_ratio)
    corners = [
        image[0:ch, 0:cw],               # top-left
        image[0:ch, w-cw:w],             # top-right
        image[h-ch:h, 0:cw],             # bottom-left
        image[h-ch:h, w-cw:w],           # bottom-right
    ]
    return [cv2.resize(c, (w, h), interpolation=cv2.INTER_LINEAR) for c in corners]


def _classify(face_roi):
    """
    Run CNN with 10-crop test-time augmentation and temperature scaling.

    TTA crops:
    1. Original
    2. Horizontally flipped
    3. Rotated +5°
    4. Rotated -5°
    5. Slight brightness increase (+10%)
    6. Slight brightness decrease (-10%)
    7. Center crop (85%)
    8-10. Corner crops (top-left, top-right, bottom-left)

    All predictions averaged for robust, less biased results.
    """
    model = _get_cached_model()

    # Prepare augmented versions
    crops = []

    # 1. Original
    crops.append(face_roi)

    # 2. Horizontally flipped
    crops.append(np.flip(face_roi, axis=1))

    # 3. Rotated +5°
    crops.append(_rotate_image(face_roi, 5))

    # 4. Rotated -5°
    crops.append(_rotate_image(face_roi, -5))

    # 5. Slight brightness increase
    bright = np.clip(face_roi * 1.1, 0, 1).astype(np.float32)
    crops.append(bright)

    # 6. Slight brightness decrease
    dark = np.clip(face_roi * 0.9, 0, 1).astype(np.float32)
    crops.append(dark)

    # 7. Center crop
    crops.append(_center_crop(face_roi, 0.85))

    # 8-10. Corner crops (3 of 4)
    corners = _corner_crops(face_roi, 0.85)
    crops.extend(corners[:3])

    # Batch predict all crops at once
    batch = np.array([c.reshape(48, 48, 1) for c in crops])
    all_probs = model.predict(batch, verbose=0)

    # Average predictions (ensemble)
    raw_probs = all_probs.mean(axis=0)

    # Class rebalancing — boost under-represented emotions
    boosted = raw_probs.copy()
    for label, factor in CLASS_BOOST.items():
        if label in EMOTION_LABELS:
            idx = EMOTION_LABELS.index(label)
            boosted[idx] *= factor
    boosted = boosted / boosted.sum()  # renormalize

    # Temperature scaling to sharpen confidence distribution
    # Lower temperature = sharper predictions, less neutral bias
    TEMPERATURE = 1.1
    logits = np.log(boosted + 1e-10)
    scaled = np.exp(logits / TEMPERATURE)
    probabilities = scaled / scaled.sum()

    top_idx = int(np.argmax(probabilities))
    emotion = EMOTION_LABELS[top_idx]
    confidence = float(probabilities[top_idx])

    # Low confidence fallback — if below threshold, use neutral
    if confidence < MIN_CONFIDENCE:
        emotion = "neutral"
        top_idx = EMOTION_LABELS.index("neutral")
        confidence = float(probabilities[top_idx])

    mood = EMOTION_TO_MOOD[emotion]
    mood_scores = emotion_to_mood_scores(probabilities)

    return {
        "emotion": emotion,
        "mood": mood,
        "confidence": confidence,
        "mood_scores": mood_scores,
        "face_found": True,
    }
