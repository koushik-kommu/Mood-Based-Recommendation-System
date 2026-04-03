"""
Training Script for the Emotion Recognition CNN — Enhanced v3
Trains on FER-2013 with:
  - Label smoothing (0.1)
  - Class-weight balancing
  - Strong data augmentation
  - Cosine annealing LR with warm restarts
  - 60 epochs with early stopping (patience=12)

Usage:
    python3 -m emotion.train_model

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
    LearningRateScheduler,
    CSVLogger,
)

# Add project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from emotion.emotion_model import build_model, MODEL_PATH

# ── Dataset paths ────────────────────────────────────────────────
KAGGLEHUB_PATH = os.path.expanduser(
    "~/.cache/kagglehub/datasets/msambare/fer2013/versions/1"
)
LOCAL_DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# Hyper-parameters
IMG_SIZE = 48
BATCH_SIZE = 64
EPOCHS = 120
INITIAL_LR = 0.001


def find_dataset():
    """Locate the FER-2013 image-folder dataset."""
    for base_path in [KAGGLEHUB_PATH, LOCAL_DATA_PATH]:
        train_dir = os.path.join(base_path, "train")
        test_dir = os.path.join(base_path, "test")
        if os.path.isdir(train_dir) and os.path.isdir(test_dir):
            return train_dir, test_dir
    return None, None


def compute_class_weights(train_dir):
    """Compute class weights to handle FER-2013 imbalance."""
    class_counts = {}
    for class_name in sorted(os.listdir(train_dir)):
        class_path = os.path.join(train_dir, class_name)
        if os.path.isdir(class_path):
            count = len([f for f in os.listdir(class_path) if f.endswith(('.jpg', '.png', '.jpeg'))])
            class_counts[class_name] = count

    total = sum(class_counts.values())
    n_classes = len(class_counts)
    weights = {}
    for i, (cls, count) in enumerate(sorted(class_counts.items())):
        weights[i] = total / (n_classes * count)

    print(f"\n📊 Class distribution:")
    for cls, count in sorted(class_counts.items()):
        pct = count / total * 100
        print(f"   {cls:>10}: {count:5d} samples ({pct:.1f}%)")
    print(f"   Class weights: {weights}")
    return weights


def cosine_annealing_schedule(epoch, lr):
    """Cosine annealing with warm restarts every 20 epochs."""
    T_max = 20
    eta_min = 1e-6
    return float(eta_min + (INITIAL_LR - eta_min) * (1 + np.cos(np.pi * (epoch % T_max) / T_max)) / 2)


def train():
    """Train the enhanced emotion CNN."""
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

    # Compute class weights for imbalanced dataset
    class_weights = compute_class_weights(train_dir)

    # Aggressive data augmentation for training
    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255.0,
        rotation_range=30,
        width_shift_range=0.15,
        height_shift_range=0.15,
        horizontal_flip=True,
        zoom_range=0.2,
        shear_range=0.15,
        brightness_range=[0.7, 1.3],
        fill_mode="nearest",
        validation_split=0.15,
    )

    test_datagen = ImageDataGenerator(
        rescale=1.0 / 255.0,
    )

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

    num_classes = len(train_generator.class_indices)

    # Resume from saved model if it exists, otherwise build fresh
    RESUME_EPOCH = 83  # Set to N to resume from epoch N (loads saved model)
    if RESUME_EPOCH > 0 and os.path.exists(MODEL_PATH):
        print(f"\n🔄 Resuming training from epoch {RESUME_EPOCH}...")
        print(f"   Loading saved model: {MODEL_PATH}")
        model = tf.keras.models.load_model(MODEL_PATH)
    else:
        print("\n🛠️ Building new CNN model v3...")
        model = build_model(input_shape=(IMG_SIZE, IMG_SIZE, 1), num_classes=num_classes)

    # Compile with label smoothing and Adam optimizer
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=INITIAL_LR),
        loss=tf.keras.losses.CategoricalCrossentropy(label_smoothing=0.1),
        metrics=["accuracy"],
    )

    model.summary()

    # Callbacks
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "training_log.csv")
    callbacks = [
        ModelCheckpoint(
            MODEL_PATH, monitor="val_accuracy", save_best_only=True, verbose=1
        ),
        EarlyStopping(
            monitor="val_accuracy", patience=12, restore_best_weights=True, verbose=1
        ),
        ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=4, min_lr=1e-6, verbose=1
        ),
        LearningRateScheduler(cosine_annealing_schedule, verbose=0),
        CSVLogger(log_path, append=(RESUME_EPOCH > 0)),
    ]

    # Train with class weights
    print(f"\n🚀 Starting training (epochs {RESUME_EPOCH+1}→{EPOCHS}, cosine LR, label smoothing)...")
    history = model.fit(
        train_generator,
        validation_data=val_generator,
        epochs=EPOCHS,
        initial_epoch=RESUME_EPOCH,
        callbacks=callbacks,
        class_weight=class_weights,
        verbose=1,
    )

    # Evaluate on test set
    print("\n📊 Evaluating on test set...")
    test_loss, test_acc = model.evaluate(test_generator, verbose=0)
    print(f"   Test Accuracy: {test_acc:.4f}")
    print(f"   Test Loss:     {test_loss:.4f}")

    # Per-class accuracy and F1 scores
    print("\n📊 Per-class predictions:")
    predictions = model.predict(test_generator, verbose=0)
    pred_classes = np.argmax(predictions, axis=1)
    true_classes = test_generator.classes
    class_names = list(test_generator.class_indices.keys())

    for i, name in enumerate(class_names):
        mask = true_classes == i
        if mask.sum() > 0:
            tp = ((pred_classes == i) & (true_classes == i)).sum()
            fp = ((pred_classes == i) & (true_classes != i)).sum()
            fn = ((pred_classes != i) & (true_classes == i)).sum()
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
            acc = (pred_classes[mask] == i).mean()
            print(f"   {name:>10}: Acc={acc:.1%}  P={precision:.3f}  R={recall:.3f}  F1={f1:.3f}  ({mask.sum()} samples)")

    print(f"\n✅ Model saved to {MODEL_PATH}")
    return history


if __name__ == "__main__":
    train()
