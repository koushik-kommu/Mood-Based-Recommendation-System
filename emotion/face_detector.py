"""
Face Detection Module
Uses OpenCV's Haar Cascade Classifier to detect and preprocess faces.
"""

import cv2
import numpy as np
import os


# Path to Haar Cascade XML (bundled with OpenCV)
CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

# Target size for the emotion CNN input
TARGET_SIZE = (48, 48)


def load_cascade():
    """Load the Haar Cascade face detector."""
    cascade = cv2.CascadeClassifier(CASCADE_PATH)
    if cascade.empty():
        raise RuntimeError("Failed to load Haar Cascade classifier.")
    return cascade


def detect_face(image_path):
    """
    Detect the largest face in an image and return the preprocessed patch.

    Parameters
    ----------
    image_path : str
        Path to the input image file.

    Returns
    -------
    face_roi : np.ndarray or None
        Preprocessed face region (48x48, normalized 0-1), or None if no face found.
    original : np.ndarray
        The original BGR image.
    face_coords : tuple or None
        (x, y, w, h) of the detected face bounding box.
    """
    # Read image
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")

    # Convert to grayscale for face detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces
    cascade = load_cascade()
    faces = cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE,
    )

    if len(faces) == 0:
        return None, image, None

    # Select the largest face (by area)
    largest = max(faces, key=lambda rect: rect[2] * rect[3])
    x, y, w, h = largest

    # Crop and preprocess
    face_roi = gray[y : y + h, x : x + w]
    face_roi = preprocess_face(face_roi)

    return face_roi, image, (x, y, w, h)


def detect_face_from_bytes(image_bytes):
    """
    Detect face from raw image bytes (e.g., from a webcam capture).

    Parameters
    ----------
    image_bytes : bytes
        Raw image data.

    Returns
    -------
    Same as detect_face().
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Could not decode image from bytes.")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cascade = load_cascade()
    faces = cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )

    if len(faces) == 0:
        return None, image, None

    largest = max(faces, key=lambda rect: rect[2] * rect[3])
    x, y, w, h = largest
    face_roi = gray[y : y + h, x : x + w]
    face_roi = preprocess_face(face_roi)

    return face_roi, image, (x, y, w, h)


def preprocess_face(face_gray):
    """
    Resize to 48x48 and normalize pixel values to [0, 1].

    Parameters
    ----------
    face_gray : np.ndarray
        Grayscale face crop of arbitrary size.

    Returns
    -------
    np.ndarray
        Shape (48, 48), dtype float32, values in [0, 1].
    """
    face_resized = cv2.resize(face_gray, TARGET_SIZE, interpolation=cv2.INTER_AREA)
    face_normalized = face_resized.astype("float32") / 255.0
    return face_normalized
