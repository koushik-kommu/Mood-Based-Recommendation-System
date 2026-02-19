"""
Training Script for the Emotion Recognition CNN
Trains on the FER-2013 dataset (image-folder format).

Usage:
    1. The dataset is auto-downloaded via kagglehub, OR
       manually download from: https://www.kaggle.com/datasets/msambare/fer2013
    2. Run:  python3 -m emotion.train_model

The trained model will be saved to: emotion/emotion_model.h5
"""

import os
import sys

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import (
    ModelCheckpoint,
    EarlyStopping,
    ReduceLROnPlateau,
)

# Add project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from emotion.emotion_model import build_model, MODEL_PATH

# ── Dataset paths ────────────────────────────────────────────────
# Try kagglehub cache first, then local emotion/data/ folder
KAGGLEHUB_PATH = os.path.expanduser(
    "~/.cache/kagglehub/datasets/msambare/fer2013/versions/1"
)
LOCAL_DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# Hyper-parameters
IMG_SIZE = 48
BATCH_SIZE = 64
EPOCHS = 30  # With early stopping, usually completes in ~15-20


def find_dataset():
    """Locate the FER-2013 image-folder dataset."""
    for base_path in [KAGGLEHUB_PATH, LOCAL_DATA_PATH]:
        train_dir = os.path.join(base_path, "train")
        test_dir = os.path.join(base_path, "test")
        if os.path.isdir(train_dir) and os.path.isdir(test_dir):
            return train_dir, test_dir

    return None, None


def train():
    """Train the emotion CNN and save the best model."""
    train_dir, test_dir = find_dataset()

    if train_dir is None:
        print("❌ FER-2013 dataset not found!")
        print("   Trying to download via kagglehub...")
        try:
            import kagglehub
            path = kagglehub.dataset_download("msambare/fer2013")
            print(f"   Downloaded to: {path}")
            train_dir = os.path.join(path, "train")
            test_dir = os.path.join(path, "test")
        except Exception as e:
            print(f"   Download failed: {e}")
            print("   Please download manually from:")
            print("   https://www.kaggle.com/datasets/msambare/fer2013")
            sys.exit(1)

    print(f"📂 Training data: {train_dir}")
    print(f"📂 Test data:     {test_dir}")

    # Data generators with augmentation for training
    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255.0,
        rotation_range=15,
        width_shift_range=0.1,
        height_shift_range=0.1,
        horizontal_flip=True,
        zoom_range=0.1,
        validation_split=0.15,  # Use 15% of training data for validation
    )

    test_datagen = ImageDataGenerator(rescale=1.0 / 255.0)

    # Load training data
    print("\n📊 Loading training data...")
    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=(IMG_SIZE, IMG_SIZE),
        color_mode="grayscale",
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        subset="training",
        shuffle=True,
    )

    # Load validation data
    val_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=(IMG_SIZE, IMG_SIZE),
        color_mode="grayscale",
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        subset="validation",
        shuffle=False,
    )

    # Load test data
    test_generator = test_datagen.flow_from_directory(
        test_dir,
        target_size=(IMG_SIZE, IMG_SIZE),
        color_mode="grayscale",
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        shuffle=False,
    )

    print(f"\n   Classes: {train_generator.class_indices}")
    print(f"   Training samples:   {train_generator.samples}")
    print(f"   Validation samples: {val_generator.samples}")
    print(f"   Test samples:       {test_generator.samples}")

    # Build model
    num_classes = len(train_generator.class_indices)
    model = build_model(input_shape=(IMG_SIZE, IMG_SIZE, 1), num_classes=num_classes)
    model.summary()

    # Callbacks
    callbacks = [
        ModelCheckpoint(
            MODEL_PATH, monitor="val_accuracy", save_best_only=True, verbose=1
        ),
        EarlyStopping(
            monitor="val_accuracy", patience=8, restore_best_weights=True
        ),
        ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=4, min_lr=1e-6, verbose=1
        ),
    ]

    # Train
    print("\n🚀 Starting training...")
    history = model.fit(
        train_generator,
        validation_data=val_generator,
        epochs=EPOCHS,
        callbacks=callbacks,
        verbose=1,
    )

    # Evaluate on test set
    print("\n📊 Evaluating on test set...")
    test_loss, test_acc = model.evaluate(test_generator, verbose=0)
    print(f"   Test Accuracy: {test_acc:.4f}")
    print(f"   Test Loss:     {test_loss:.4f}")

    print(f"\n✅ Model saved to {MODEL_PATH}")

    return history


if __name__ == "__main__":
    train()
