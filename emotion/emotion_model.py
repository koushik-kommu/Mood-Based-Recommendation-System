"""
Emotion CNN Model Definition — Enhanced v2
Optimized CNN with Squeeze-and-Excitation attention for improved
facial emotion recognition on 48×48 grayscale images.
Architecture: 3 Conv blocks (64→128→256) + SE + GAP → Dense → Softmax (7 classes)
Optimized for CPU training convergence on FER-2013.
"""

import os
import numpy as np

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import tensorflow as tf
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import (
    Conv2D, BatchNormalization, MaxPooling2D, Dropout, Dense, Input,
    GlobalAveragePooling2D, Multiply, Reshape, Flatten,
)
from tensorflow.keras.regularizers import l2

EMOTION_LABELS = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]

EMOTION_TO_MOOD = {
    "angry": "angry",
    "disgust": "angry",
    "fear": "stressed",
    "happy": "happy",
    "sad": "sad",
    "surprise": "excited",
    "neutral": "neutral",
}

MOOD_CATEGORIES = [
    "happy", "sad", "angry", "neutral", "excited", "stressed",
    "romantic", "motivational", "calm", "energetic",
]

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(MODEL_DIR, "emotion_model.h5")

WEIGHT_DECAY = 1e-4


def _se_block(x, ratio=8):
    """Squeeze-and-Excitation attention — learns channel importance."""
    filters = x.shape[-1]
    se = GlobalAveragePooling2D()(x)
    se = Reshape((1, 1, filters))(se)
    se = Dense(filters // ratio, activation="relu")(se)
    se = Dense(filters, activation="sigmoid")(se)
    return Multiply()([x, se])


def _conv_block(x, filters, dropout_rate=0.25):
    """Double-conv block with batch norm, SE attention, and dropout."""
    x = Conv2D(filters, (3, 3), activation="relu", padding="same",
               kernel_regularizer=l2(WEIGHT_DECAY))(x)
    x = BatchNormalization()(x)
    x = Conv2D(filters, (3, 3), activation="relu", padding="same",
               kernel_regularizer=l2(WEIGHT_DECAY))(x)
    x = BatchNormalization()(x)
    x = _se_block(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)
    x = Dropout(dropout_rate)(x)
    return x


def build_model(input_shape=(48, 48, 1), num_classes=7):
    """
    Build optimized CNN with SE attention for FER-2013.

    Architecture:
        Block 1 (64):  Conv→BN→Conv→BN→SE→Pool→Drop — 48×48 → 24×24
        Block 2 (128): Conv→BN→Conv→BN→SE→Pool→Drop — 24×24 → 12×12
        Block 3 (256): Conv→BN→Conv→BN→SE→Pool→Drop — 12×12 → 6×6
        Flatten → Dense(512) → BN → Drop(0.5) → Dense(7, softmax)
    """
    inputs = Input(shape=input_shape)

    x = _conv_block(inputs, 64, dropout_rate=0.25)   # → 24×24
    x = _conv_block(x, 128, dropout_rate=0.25)        # → 12×12
    x = _conv_block(x, 256, dropout_rate=0.25)        # → 6×6

    x = Flatten()(x)
    x = Dense(512, activation="relu", kernel_regularizer=l2(WEIGHT_DECAY))(x)
    x = BatchNormalization()(x)
    x = Dropout(0.5)(x)

    outputs = Dense(num_classes, activation="softmax")(x)

    model = Model(inputs=inputs, outputs=outputs, name="EmotionCNN_SE_v2")
    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def get_model():
    """Load trained model or build new one."""
    if os.path.exists(MODEL_PATH):
        try:
            model = load_model(MODEL_PATH)
            return model
        except Exception as e:
            print(f"⚠️  Could not load model ({e}). Building new one.")
    print("⚠️  No trained model found. Run: python -m emotion.train_model")
    return build_model()


def emotion_to_mood_scores(probabilities):
    """Convert 7-class FER probabilities into mood-category scores."""
    mood_scores = {mood: 0.0 for mood in MOOD_CATEGORIES}
    for i, emotion in enumerate(EMOTION_LABELS):
        target_mood = EMOTION_TO_MOOD[emotion]
        mood_scores[target_mood] += float(probabilities[i])
    return mood_scores
