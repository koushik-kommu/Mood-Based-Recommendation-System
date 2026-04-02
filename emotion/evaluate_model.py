"""
Dry-Run Evaluation Script — No Retraining Required
Loads the saved emotion_model.h5 and evaluates on FER-2013 test set.
Prints terminal-style epoch simulation, per-class metrics, and confusion matrix.
"""

import os, sys
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from emotion.emotion_model import MODEL_PATH

# ── Paths ────────────────────────────────────────────────────────
KAGGLEHUB_PATH = os.path.expanduser(
    "~/.cache/kagglehub/datasets/msambare/fer2013/versions/1"
)
LOCAL_DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
IMG_SIZE = 48
BATCH_SIZE = 64


def find_dataset():
    for base in [KAGGLEHUB_PATH, LOCAL_DATA_PATH]:
        train_dir = os.path.join(base, "train")
        test_dir = os.path.join(base, "test")
        if os.path.isdir(train_dir) and os.path.isdir(test_dir):
            return train_dir, test_dir
    return None, None


def evaluate():
    print("=" * 70)
    print("  EMOTION RECOGNITION MODEL — DRY-RUN EVALUATION")
    print("  (No retraining — using saved weights)")
    print("=" * 70)

    # ── Load model ───────────────────────────────────────────────
    if not os.path.exists(MODEL_PATH):
        print(f"\n❌ Model file not found: {MODEL_PATH}")
        sys.exit(1)

    print(f"\n📂 Loading model from: {MODEL_PATH}")
    model = tf.keras.models.load_model(MODEL_PATH)
    total_params = model.count_params()
    print(f"   Parameters: {total_params:,}")
    print(f"   Input shape: {model.input_shape}")
    print(f"   Output classes: {model.output_shape[-1]}")

    # ── Load dataset ─────────────────────────────────────────────
    train_dir, test_dir = find_dataset()
    if test_dir is None:
        print("\n❌ FER-2013 dataset not found!")
        print("   Expected at:", KAGGLEHUB_PATH)
        print("   Or at:", LOCAL_DATA_PATH)
        sys.exit(1)

    print(f"\n📂 Dataset: {os.path.dirname(test_dir)}")

    test_datagen = ImageDataGenerator(rescale=1.0 / 255.0)

    test_gen = test_datagen.flow_from_directory(
        test_dir,
        target_size=(IMG_SIZE, IMG_SIZE),
        color_mode="grayscale",
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        shuffle=False,
    )

    class_names = list(test_gen.class_indices.keys())
    n_classes = len(class_names)

    # Also load train set for class distribution
    train_gen = test_datagen.flow_from_directory(
        train_dir,
        target_size=(IMG_SIZE, IMG_SIZE),
        color_mode="grayscale",
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        shuffle=False,
    )

    # ── Class distribution ───────────────────────────────────────
    print(f"\n{'─' * 70}")
    print("  📊 TRAINING CLASS DISTRIBUTION")
    print(f"{'─' * 70}")
    train_counts = {}
    for cls_name in sorted(os.listdir(train_dir)):
        cls_path = os.path.join(train_dir, cls_name)
        if os.path.isdir(cls_path):
            count = len([f for f in os.listdir(cls_path) if f.endswith(('.jpg', '.png', '.jpeg'))])
            train_counts[cls_name] = count

    total_train = sum(train_counts.values())
    for cls, count in sorted(train_counts.items()):
        pct = count / total_train * 100
        bar = "█" * int(pct / 2) + "░" * (25 - int(pct / 2))
        print(f"  {cls:>10}: {count:5d} ({pct:5.1f}%) {bar}")
    print(f"  {'Total':>10}: {total_train:5d}")

    # ── Model evaluation ─────────────────────────────────────────
    print(f"\n{'─' * 70}")
    print("  🧪 EVALUATING ON TEST SET...")
    print(f"{'─' * 70}")
    print(f"  Test samples: {test_gen.samples}")
    print(f"  Batches: {len(test_gen)}")
    print()

    test_loss, test_acc = model.evaluate(test_gen, verbose=1)

    print(f"\n  ┌─────────────────────────────┐")
    print(f"  │  Test Accuracy:  {test_acc:.4f}     │")
    print(f"  │  Test Loss:      {test_loss:.4f}     │")
    print(f"  └─────────────────────────────┘")

    # ── Predictions ──────────────────────────────────────────────
    print(f"\n{'─' * 70}")
    print("  📊 PER-CLASS METRICS")
    print(f"{'─' * 70}")

    predictions = model.predict(test_gen, verbose=0)
    pred_classes = np.argmax(predictions, axis=1)
    true_classes = test_gen.classes

    print(f"\n  {'Class':>10} │ {'Acc':>6} │ {'Prec':>6} │ {'Recall':>6} │ {'F1':>6} │ {'Samples':>7}")
    print(f"  {'─' * 10}─┼{'─' * 8}┼{'─' * 8}┼{'─' * 8}┼{'─' * 8}┼{'─' * 9}")

    per_class_acc = []
    for i, name in enumerate(class_names):
        mask = true_classes == i
        n_samples = mask.sum()
        if n_samples == 0:
            continue

        tp = ((pred_classes == i) & (true_classes == i)).sum()
        fp = ((pred_classes == i) & (true_classes != i)).sum()
        fn = ((pred_classes != i) & (true_classes == i)).sum()

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        acc = (pred_classes[mask] == i).mean()
        per_class_acc.append(acc)

        print(f"  {name:>10} │ {acc:5.1%} │ {precision:6.3f} │ {recall:6.3f} │ {f1:6.3f} │ {n_samples:7d}")

    print(f"  {'─' * 10}─┼{'─' * 8}┼{'─' * 8}┼{'─' * 8}┼{'─' * 8}┼{'─' * 9}")
    avg_acc = np.mean(per_class_acc)
    print(f"  {'Average':>10} │ {avg_acc:5.1%} │        │        │        │ {test_gen.samples:7d}")

    # ── Confusion Matrix ─────────────────────────────────────────
    print(f"\n{'─' * 70}")
    print("  📋 CONFUSION MATRIX")
    print(f"{'─' * 70}")

    cm = np.zeros((n_classes, n_classes), dtype=int)
    for t, p in zip(true_classes, pred_classes):
        cm[t][p] += 1

    # Header
    header = "  Actual\\Pred │ " + " │ ".join(f"{n[:4]:>4}" for n in class_names) + " │"
    print(f"\n{header}")
    print(f"  {'─' * 14}┼" + "┼".join(["─" * 6] * n_classes) + "┤")

    for i, name in enumerate(class_names):
        row = f"  {name:>12} │ "
        for j in range(n_classes):
            val = cm[i][j]
            if i == j:
                row += f"\033[1;32m{val:4d}\033[0m │ "  # green for diagonal
            elif val > 0:
                row += f"{val:4d} │ "
            else:
                row += f"   . │ "
        print(row)

    # ── Summary ──────────────────────────────────────────────────
    print(f"\n{'═' * 70}")
    print(f"  ✅ EVALUATION COMPLETE")
    print(f"     Model: {MODEL_PATH}")
    print(f"     Overall Test Accuracy: {test_acc:.2%}")
    print(f"     Best class:  {class_names[np.argmax(per_class_acc)]} ({max(per_class_acc):.1%})")
    print(f"     Worst class: {class_names[np.argmin(per_class_acc)]} ({min(per_class_acc):.1%})")
    print(f"{'═' * 70}")


if __name__ == "__main__":
    evaluate()
