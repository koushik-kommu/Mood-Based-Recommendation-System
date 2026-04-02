"""
Emotion CNN Model Definition — Enhanced v3
Deeper CNN with residual-style skip connections, Squeeze-and-Excitation
attention, and Global Average Pooling for robust emotion recognition.

Architecture: 4 Conv blocks (64→128→256→512) + SE + GAP → Dense → Softmax (7 classes)
Optimized for FER-2013 with better regularization and capacity.
"""

import os
import numpy as np

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import tensorflow as tf
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import (
    Conv2D, BatchNormalization, MaxPooling2D, Dropout, Dense, Input,
    GlobalAveragePooling2D, Multiply, Reshape, Flatten, Add,
    DepthwiseConv2D, Activation,
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
    "happy", "sad", "angry", "neutral", "excited", "stressed", "calm",
]

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(MODEL_DIR, "emotion_model.h5")

WEIGHT_DECAY = 5e-5


def _se_block(x, ratio=8):
    """Squeeze-and-Excitation attention — learns channel importance."""
    filters = x.shape[-1]
    se = GlobalAveragePooling2D()(x)
    se = Reshape((1, 1, filters))(se)
    se = Dense(filters // ratio, activation="relu",
               kernel_regularizer=l2(WEIGHT_DECAY))(se)
    se = Dense(filters, activation="sigmoid")(se)
    return Multiply()([x, se])


def _conv_block(x, filters, dropout_rate=0.25):
    """
    Enhanced conv block: Conv→BN→ReLU→Conv→BN→ReLU→SE→Pool→Drop
    With residual shortcut when spatial dims allow.
    """
    shortcut = x

    x = Conv2D(filters, (3, 3), padding="same",
               kernel_regularizer=l2(WEIGHT_DECAY))(x)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)

    x = Conv2D(filters, (3, 3), padding="same",
               kernel_regularizer=l2(WEIGHT_DECAY))(x)
    x = BatchNormalization()(x)

    # Residual connection if shapes match
    if shortcut.shape[-1] == filters:
        x = Add()([x, shortcut])

    x = Activation("relu")(x)
    x = _se_block(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)
    x = Dropout(dropout_rate)(x)
    return x


def build_model(input_shape=(48, 48, 1), num_classes=7):
    """
    Build enhanced CNN v3 with SE attention and residual connections.

    Architecture:
        Block 1 (64):  Conv→BN→ReLU→Conv→BN→ReLU→SE→Pool→Drop  48→24
        Block 2 (128): Conv→BN→ReLU→Conv→BN→ReLU→SE→Pool→Drop  24→12
        Block 3 (256): Conv→BN→ReLU→Conv→BN→ReLU→SE→Pool→Drop  12→6
        Block 4 (512): Conv→BN→ReLU→Conv→BN→ReLU→SE→Pool→Drop  6→3
        GAP → Dense(256) → BN → Drop → Dense(128) → BN → Drop → Dense(7, softmax)
    """
    inputs = Input(shape=input_shape)

    x = _conv_block(inputs, 64, dropout_rate=0.25)    # → 24×24
    x = _conv_block(x, 128, dropout_rate=0.25)        # → 12×12
    x = _conv_block(x, 256, dropout_rate=0.30)        # → 6×6
    x = _conv_block(x, 512, dropout_rate=0.40)        # → 3×3

    # Global Average Pooling instead of Flatten (more robust, less overfitting)
    x = GlobalAveragePooling2D()(x)

    # Two dense layers with batch norm for better feature extraction
    x = Dense(256, activation="relu", kernel_regularizer=l2(WEIGHT_DECAY))(x)
    x = BatchNormalization()(x)
    x = Dropout(0.5)(x)

    x = Dense(128, activation="relu", kernel_regularizer=l2(WEIGHT_DECAY))(x)
    x = BatchNormalization()(x)
    x = Dropout(0.4)(x)

    outputs = Dense(num_classes, activation="softmax")(x)

    model = Model(inputs=inputs, outputs=outputs, name="EmotionCNN_SE_v3")
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
