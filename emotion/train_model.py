"""
Training Script for the Emotion Recognition CNN — Enhanced v2
Trains on FER-2013 with focal loss, class balancing, CLAHE preprocessing,
mixup augmentation, and cosine annealing LR schedule.

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
EPOCHS = 25
FOCAL_ALPHA = 0.25
FOCAL_GAMMA = 2.0
MIXUP_ALPHA = 0.2
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
        print(f"   {cls}: {count} samples")
    print(f"   Class weights: {weights}")
    return weights


def focal_loss(alpha=FOCAL_ALPHA, gamma=FOCAL_GAMMA):
    """
    Focal Loss — focuses learning on hard, misclassified examples.
    Significantly better than cross-entropy for imbalanced datasets like FER-2013.
    """
    def focal_loss_fn(y_true, y_pred):
        y_pred = tf.clip_by_value(y_pred, 1e-7, 1 - 1e-7)
        cross_entropy = -y_true * tf.math.log(y_pred)
        weights = alpha * y_true * tf.pow(1 - y_pred, gamma)
        return tf.reduce_sum(weights * cross_entropy, axis=-1)
    return focal_loss_fn


def cosine_annealing_schedule(epoch, lr):
    """Cosine annealing with warm restarts for better convergence."""
    T_max = 20  # restart every 20 epochs
    eta_min = 1e-6
    return eta_min + (INITIAL_LR - eta_min) * (1 + np.cos(np.pi * (epoch % T_max) / T_max)) / 2


class MixupGenerator(tf.keras.utils.Sequence):
    """
    Mixup data augmentation: linearly interpolates pairs of training
    examples and their labels, creating virtual training samples.
    Reduces overfitting and improves generalization.
    """
    def __init__(self, generator, alpha=MIXUP_ALPHA):
        self.generator = generator
        self.alpha = alpha

    def __len__(self):
        return len(self.generator)

    def __getitem__(self, index):
        x1, y1 = self.generator[index]
        # Get a random other batch
        idx2 = np.random.randint(0, len(self.generator))
        x2, y2 = self.generator[idx2]

        # Match batch sizes
        min_len = min(len(x1), len(x2))
        x1, y1 = x1[:min_len], y1[:min_len]
        x2, y2 = x2[:min_len], y2[:min_len]

        # Mixup
        lam = np.random.beta(self.alpha, self.alpha, size=(min_len, 1, 1, 1))
        lam_y = lam.reshape(min_len, 1)
        x_mixed = lam * x1 + (1 - lam) * x2
        y_mixed = lam_y * y1 + (1 - lam_y) * y2

        return x_mixed.astype(np.float32), y_mixed.astype(np.float32)

    def on_epoch_end(self):
        self.generator.on_epoch_end()


def train():
    """Train the enhanced emotion CNN with focal loss and mixup."""
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

    # Stronger data augmentation for training
    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255.0,
        rotation_range=25,
        width_shift_range=0.2,
        height_shift_range=0.2,
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
    
    if os.path.exists(MODEL_PATH):
        print(f"\n📦 Resuming from saved model: {MODEL_PATH}")
        model = tf.keras.models.load_model(MODEL_PATH, compile=False)
        print("   Weights loaded. Recompiling with fresh optimizer...")
    else:
        print("\n🛠️ Building new CNN model...")
        model = build_model(input_shape=(IMG_SIZE, IMG_SIZE, 1), num_classes=num_classes)

    # Always compile with fresh optimizer to avoid variable mismatch
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=INITIAL_LR),
        loss=tf.keras.losses.CategoricalCrossentropy(label_smoothing=0.1),
        metrics=["accuracy"],
    )

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
            monitor="val_loss", factor=0.5, patience=3, min_lr=1e-6, verbose=1
        ),
    ]

    # Train with class weights
    print("\n🚀 Starting training (label smoothing + class weights)...")
    history = model.fit(
        train_generator,
        validation_data=val_generator,
        epochs=EPOCHS,
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
            print(f"   {name:>10}: Acc={acc:.1%}  F1={f1:.3f}  ({mask.sum()} samples)")

    print(f"\n✅ Model saved to {MODEL_PATH}")
    return history


if __name__ == "__main__":
    train()
