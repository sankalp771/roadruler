import cv2
import numpy as np

from ai_engine.quality_filter import assess_image_quality


def _encode(image: np.ndarray) -> bytes:
    success, encoded = cv2.imencode(".jpg", image)
    assert success
    return encoded.tobytes()


def test_quality_filter_accepts_sharp_road_photo():
    rng = np.random.default_rng(27)
    image = rng.integers(40, 180, size=(160, 160, 3), dtype=np.uint8)

    result = assess_image_quality(_encode(image))

    assert result.is_valid is True
    assert result.reason is None
    assert result.metrics["laplacian_variance"] >= 60


def test_quality_filter_rejects_blurred_photo():
    rng = np.random.default_rng(27)
    image = rng.integers(40, 180, size=(160, 160, 3), dtype=np.uint8)
    blurred = cv2.GaussianBlur(image, (31, 31), 0)

    result = assess_image_quality(_encode(blurred))

    assert result.is_valid is False
    assert result.reason == "BLURRY_IMAGE"


def test_quality_filter_rejects_dark_and_undecodable_uploads():
    dark = np.full((64, 64, 3), 8, dtype=np.uint8)

    dark_result = assess_image_quality(_encode(dark))
    invalid_result = assess_image_quality(b"not an image")

    assert dark_result.reason == "TOO_DARK"
    assert invalid_result.reason == "INVALID_IMAGE"
