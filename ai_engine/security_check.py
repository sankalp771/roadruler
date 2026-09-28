"""Validate image uploads before any decoder or storage service receives them."""

from dataclasses import dataclass
from io import BytesIO

from PIL import Image

MAX_IMAGE_DIMENSION = 4096
MAX_IMAGE_PIXELS = MAX_IMAGE_DIMENSION * MAX_IMAGE_DIMENSION

_SIGNATURES = {
    "JPEG": lambda data: data.startswith(b"\xff\xd8\xff"),
    "PNG": lambda data: data.startswith(b"\x89PNG\r\n\x1a\n"),
    "WEBP": lambda data: len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP",
}
_MIME_FORMATS = {"image/jpeg": "JPEG", "image/png": "PNG", "image/webp": "WEBP"}


@dataclass(frozen=True)
class ImageSecurityAssessment:
    is_secure: bool
    reason: str | None = None
    image_format: str | None = None
    width: int | None = None
    height: int | None = None


def assess_image_security(image_bytes: bytes, content_type: str | None = None) -> ImageSecurityAssessment:
    """Check declared MIME, file signature, decoded format, and dimensions."""
    if not image_bytes:
        return ImageSecurityAssessment(False, "EMPTY_FILE")

    detected_format = next((fmt for fmt, matches in _SIGNATURES.items() if matches(image_bytes)), None)
    if detected_format is None:
        return ImageSecurityAssessment(False, "INVALID_IMAGE_SIGNATURE")
    if content_type and _MIME_FORMATS.get(content_type.lower()) != detected_format:
        return ImageSecurityAssessment(False, "CONTENT_TYPE_MISMATCH", detected_format)

    try:
        with Image.open(BytesIO(image_bytes)) as image:
            if image.format != detected_format:
                return ImageSecurityAssessment(False, "IMAGE_FORMAT_MISMATCH", detected_format)
            width, height = image.size
            if width < 1 or height < 1 or width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION or width * height > MAX_IMAGE_PIXELS:
                return ImageSecurityAssessment(False, "IMAGE_DIMENSIONS_EXCEEDED", detected_format, width, height)
            image.verify()
    except Exception:
        # Pillow may be wrapped by optional decoder plugins; corrupt input must fail
        # closed even if an installed plugin itself is unavailable.
        return ImageSecurityAssessment(False, "CORRUPT_IMAGE", detected_format)

    return ImageSecurityAssessment(True, None, detected_format, width, height)
