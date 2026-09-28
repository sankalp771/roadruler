"""Lightweight image decoding and quality checks for citizen uploads."""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class ImageQualityAssessment:
    is_valid: bool
    reason: Optional[str]
    metrics: Dict[str, float]


def assess_image_quality(image_bytes: bytes, blur_threshold: float = 60.0, darkness_threshold: float = 20.0) -> ImageQualityAssessment:
    """Decode the image and check blur and darkness before expensive inference."""
    if not image_bytes:
        return ImageQualityAssessment(False, "INVALID_IMAGE", {})

    try:
        import cv2
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("OpenCV is required to assess uploaded image quality") from exc

    encoded = np.frombuffer(image_bytes, dtype=np.uint8)
    try:
        image = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    except cv2.error:
        image = None

    if image is None or image.size == 0:
        return ImageQualityAssessment(False, "INVALID_IMAGE", {})

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur_variance = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    mean_intensity = float(gray.mean())
    metrics = {
        "laplacian_variance": round(blur_variance, 3),
        "mean_intensity": round(mean_intensity, 3),
    }
    if mean_intensity < darkness_threshold:
        return ImageQualityAssessment(False, "TOO_DARK", metrics)
    if blur_variance < blur_threshold:
        return ImageQualityAssessment(False, "BLURRY_IMAGE", metrics)
    return ImageQualityAssessment(True, None, metrics)
