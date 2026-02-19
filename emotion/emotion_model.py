"""
Emotion CNN Model Definition
A lightweight Convolutional Neural Network for facial emotion recognition.
Architecture: 3 Conv blocks → Dense → Softmax (7 classes)
"""

import os
import numpy as np

# Suppress TensorFlow info logs
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import (
    Conv2D,
    BatchNormalization,
    MaxPooling2D,
    Dropout,
    Flatten,
    Dense,
    Input,
)

# Emotion labels aligned with FER-2013 dataset
EMOTION_LABELS = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]

#  Map 7 FER classes → 6 project mood categories
EMOTION_TO_MOOD = {
    "angry": "angry",
    "disgust": "angry",      # merge disgust into angry
    "fear": "stressed",      # fear maps to stressed
    "happy": "happy",
    "sad": "sad",
    "surprise": "excited",   # surprise maps to excited
    "neutral": "neutral",
}

# All mood categories used in the project
MOOD_CATEGORIES = ["happy", "sad", "angry", "neutral", "excited", "stressed"]

# Path to saved model weights
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(MODEL_DIR, "emotion_model.h5")


def build_model(input_shape=(48, 48, 1), num_classes=7):
    """
    Build the lightweight CNN for emotion classification.

    Architecture:
        Conv2D(32) → BN → MaxPool → Dropout
        Conv2D(64) → BN → MaxPool → Dropout
        Conv2D(128) → BN → MaxPool → Dropout
        Flatten → Dense(256) → Dropout → Dense(7, softmax)
    """
    model = Sequential([
        Input(shape=input_shape),

        # Block 1
        Conv2D(32, (3, 3), activation="relu", padding="same"),
        BatchNormalization(),
        MaxPooling2D(pool_size=(2, 2)),
        Dropout(0.25),

        # Block 2
        Conv2D(64, (3, 3), activation="relu", padding="same"),
        BatchNormalization(),
        MaxPooling2D(pool_size=(2, 2)),
        Dropout(0.25),

        # Block 3
        Conv2D(128, (3, 3), activation="relu", padding="same"),
        BatchNormalization(),
        MaxPooling2D(pool_size=(2, 2)),
        Dropout(0.25),

        # Classifier
        Flatten(),
        Dense(256, activation="relu"),
        BatchNormalization(),
        Dropout(0.5),
        Dense(num_classes, activation="softmax"),
    ])

    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    return model


def get_model():
    """
    Load the trained model if it exists, otherwise build a new one.
    """
    if os.path.exists(MODEL_PATH):
        model = load_model(MODEL_PATH)
        return model
    else:
        print("⚠️  No trained model found. Building a new model.")
        print(f"   Train it by running: python -m emotion.train_model")
        model = build_model()
        return model


def emotion_to_mood_scores(probabilities):
    """
    Convert 7-class FER probabilities into 6 mood-category scores.

    Parameters
    ----------
    probabilities : np.ndarray
        Shape (7,) — raw softmax outputs from the CNN.

    Returns
    -------
    dict
        {mood_category: score} for each of the 6 moods.
    """
    mood_scores = {mood: 0.0 for mood in MOOD_CATEGORIES}
    for i, emotion in enumerate(EMOTION_LABELS):
        target_mood = EMOTION_TO_MOOD[emotion]
        mood_scores[target_mood] += float(probabilities[i])
    return mood_scores
