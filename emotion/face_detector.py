"""
Face Detection Module — Enhanced v3
Multi-backend detector: Haar Cascade (primary) → OpenCV DNN (fallback).
Improved preprocessing with bilateral filtering, adaptive gamma correction,
dual CLAHE, and histogram stretching for robust emotion recognition.
"""

import cv2
import numpy as np
import os

# ── Detector Paths ───────────────────────────────────────────────
CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

# DNN face detector (ships with OpenCV)
_DNN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dnn")
DNN_PROTO = os.path.join(_DNN_DIR, "deploy.prototxt")
DNN_MODEL = os.path.join(_DNN_DIR, "res10_300x300_ssd_iter_140000.caffemodel")

TARGET_SIZE = (48, 48)
FACE_PADDING = 0.18  # 18% padding for better context

# ── Singleton Loaders ────────────────────────────────────────────
_cascade = None
_dnn_net = None


def _get_cascade():
    global _cascade
    if _cascade is None:
        _cascade = cv2.CascadeClassifier(CASCADE_PATH)
        if _cascade.empty():
            raise RuntimeError("Failed to load Haar Cascade classifier.")
    return _cascade


def _get_dnn_net():
    """Load the Caffe-based DNN face detector if model files exist."""
    global _dnn_net
    if _dnn_net is None:
        if os.path.exists(DNN_PROTO) and os.path.exists(DNN_MODEL):
            _dnn_net = cv2.dnn.readNetFromCaffe(DNN_PROTO, DNN_MODEL)
        else:
            _dnn_net = False  # Mark as unavailable
    return _dnn_net if _dnn_net is not False else None


# ── Public API ───────────────────────────────────────────────────

def detect_face(image_path):
    """Detect face from an image file path."""
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return _detect_in_gray(gray, image)


def detect_face_from_bytes(image_bytes):
    """Detect face from raw image bytes (webcam capture)."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Could not decode image from bytes.")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return _detect_in_gray(gray, image)


# ── Core Detection ───────────────────────────────────────────────

def _detect_in_gray(gray, original):
    """Detect largest face using cascaded strategies, return preprocessed ROI."""

    # Strategy 1: Haar Cascade (fast, works well for frontal faces)
    face_rect = _haar_detect(gray)

    # Strategy 2: DNN detector fallback (better with angles/lighting)
    if face_rect is None:
        face_rect = _dnn_detect(original)

    if face_rect is None:
        return None, original, None

    x, y, w, h = face_rect

    # Add padding for better context
    pad_w = int(w * FACE_PADDING)
    pad_h = int(h * FACE_PADDING)
    x1 = max(0, x - pad_w)
    y1 = max(0, y - pad_h)
    x2 = min(gray.shape[1], x + w + pad_w)
    y2 = min(gray.shape[0], y + h + pad_h)

    face_roi = gray[y1:y2, x1:x2]
    face_roi = preprocess_face(face_roi)

    return face_roi, original, (x, y, w, h)


def _haar_detect(gray):
    """Haar Cascade with progressive parameter relaxation."""
    cascade = _get_cascade()

    # Pass 1: strict params
    faces = cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE,
    )
    if len(faces) > 0:
        return tuple(max(faces, key=lambda r: r[2] * r[3]))

    # Pass 2: relaxed
    faces = cascade.detectMultiScale(
        gray, scaleFactor=1.05, minNeighbors=3, minSize=(20, 20),
    )
    if len(faces) > 0:
        return tuple(max(faces, key=lambda r: r[2] * r[3]))

    # Pass 3: very lenient (catches low-contrast faces)
    faces = cascade.detectMultiScale(
        gray, scaleFactor=1.03, minNeighbors=2, minSize=(15, 15),
    )
    if len(faces) > 0:
        return tuple(max(faces, key=lambda r: r[2] * r[3]))

    return None


def _dnn_detect(color_image, conf_threshold=0.5):
    """OpenCV DNN SSD face detector — better with varied lighting/angles."""
    net = _get_dnn_net()
    if net is None:
        return None

    h, w = color_image.shape[:2]
    blob = cv2.dnn.blobFromImage(
        cv2.resize(color_image, (300, 300)), 1.0, (300, 300),
        (104.0, 177.0, 123.0),
    )
    net.setInput(blob)
    detections = net.forward()

    best = None
    best_area = 0
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence < conf_threshold:
            continue
        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        x1, y1, x2, y2 = box.astype(int)
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        area = (x2 - x1) * (y2 - y1)
        if area > best_area:
            best_area = area
            best = (x1, y1, x2 - x1, y2 - y1)

    return best


# ── Preprocessing ────────────────────────────────────────────────

def preprocess_face(face_gray):
    """
    Enhanced preprocessing pipeline v3 for emotion recognition.
    Optimised for subtle emotions (sadness, disgust, fear) that
    depend on fine muscle contrasts around the eyes and mouth.

    Pipeline:
      1. Bilateral filter — denoise while preserving edges
      2. Adaptive gamma correction — normalize lighting
      3. Histogram stretching — maximise tonal range
      4. Dual CLAHE — coarse + fine contrast enhancement
      5. Light Gaussian smoothing — suppress CLAHE artifacts
      6. Resize to 48×48 and normalise to [0, 1]
    """
    # 1. Edge-preserving denoising
    face_gray = cv2.bilateralFilter(face_gray, d=7, sigmaColor=60, sigmaSpace=60)

    # 2. Adaptive gamma correction (wider range for extreme lighting)
    mean_val = np.mean(face_gray)
    if mean_val < 60:
        gamma = 0.5          # very dark → strong brighten
    elif mean_val < 100:
        gamma = 0.75         # dark → moderate brighten
    elif mean_val > 200:
        gamma = 1.8          # very bright → strong darken
    elif mean_val > 160:
        gamma = 1.3          # bright → moderate darken
    else:
        gamma = 1.0
    if gamma != 1.0:
        table = np.array([
            ((i / 255.0) ** gamma) * 255 for i in range(256)
        ]).astype("uint8")
        face_gray = cv2.LUT(face_gray, table)

    # 3. Histogram stretching — map [min, max] → [0, 255]
    pmin, pmax = np.percentile(face_gray, (2, 98))
    if pmax - pmin > 10:
        face_gray = np.clip((face_gray - pmin) * 255.0 / (pmax - pmin), 0, 255).astype(np.uint8)

    # 4. Dual CLAHE — coarse pass for global contrast, fine pass for local detail
    clahe_coarse = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(4, 4))
    face_gray = clahe_coarse.apply(face_gray)
    clahe_fine = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    face_gray = clahe_fine.apply(face_gray)

    # 5. Light Gaussian blur to suppress CLAHE noise artifacts
    face_gray = cv2.GaussianBlur(face_gray, (3, 3), 0)

    # 6. Resize and normalize
    face_resized = cv2.resize(face_gray, TARGET_SIZE, interpolation=cv2.INTER_AREA)
    face_normalized = face_resized.astype("float32") / 255.0

    return face_normalized
