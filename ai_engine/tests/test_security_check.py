from io import BytesIO

from PIL import Image

from ai_engine.security_check import assess_image_security


def _image_bytes(image_format: str, size: tuple[int, int] = (32, 24)) -> bytes:
    buffer = BytesIO()
    Image.new("RGB", size, color=(90, 120, 150)).save(buffer, format=image_format)
    return buffer.getvalue()


def test_accepts_valid_jpeg_png_and_webp_signatures():
    for image_format, content_type in (("JPEG", "image/jpeg"), ("PNG", "image/png"), ("WEBP", "image/webp")):
        assessment = assess_image_security(_image_bytes(image_format), content_type)
        assert assessment.is_secure is True
        assert assessment.image_format == image_format


def test_rejects_text_renamed_as_jpeg_and_mime_mismatch():
    disguised = assess_image_security(b"this is plain text, not an image", "image/jpeg")
    mismatch = assess_image_security(_image_bytes("PNG"), "image/jpeg")
    assert disguised.is_secure is False
    assert disguised.reason == "INVALID_IMAGE_SIGNATURE"
    assert mismatch.reason == "CONTENT_TYPE_MISMATCH"


def test_rejects_oversized_and_corrupt_images():
    oversized = assess_image_security(_image_bytes("PNG", (4097, 1)), "image/png")
    corrupt = assess_image_security(b"\xff\xd8\xffgarbage", "image/jpeg")
    assert oversized.reason == "IMAGE_DIMENSIONS_EXCEEDED"
    assert corrupt.reason == "CORRUPT_IMAGE"
