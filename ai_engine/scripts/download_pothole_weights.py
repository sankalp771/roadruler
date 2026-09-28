"""Download the pinned single-class YOLOv8 pothole model used by RoadRuler."""

import hashlib
import logging
import urllib.request
import zipfile
from pathlib import Path


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
WEIGHTS_URL = (
    "https://huggingface.co/peterhdd/pothole-detection-yolov8/resolve/"
    "101b80987b3fa86f9747d4170f936760ebad3a9f/best.pt"
)
EXPECTED_SHA256 = "af2ac6ce7bfec72e71643659ac946caf80ced84869e526a60135c457abfbb200"
OUTPUT_PATH = REPO_ROOT / "ai_engine" / "weights" / "pretrained_pothole.pt"


def download_weights() -> Path:
    """Download atomically and verify the pinned checkpoint checksum."""
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = OUTPUT_PATH.with_suffix(".pt.download")
    logger.info("Downloading pothole weights from %s", WEIGHTS_URL)

    request = urllib.request.Request(
        WEIGHTS_URL,
        headers={"User-Agent": "RoadRuler-model-setup"},
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            with temporary_path.open("wb") as output_file:
                while chunk := response.read(1024 * 1024):
                    output_file.write(chunk)

        if not zipfile.is_zipfile(temporary_path):
            raise ValueError("Downloaded file is not a valid PyTorch checkpoint archive.")

        digest = hashlib.sha256(temporary_path.read_bytes()).hexdigest()
        if digest != EXPECTED_SHA256:
            raise ValueError("Downloaded checkpoint SHA-256 does not match the pinned model.")

        temporary_path.replace(OUTPUT_PATH)
        logger.info("Pothole weights saved to %s", OUTPUT_PATH)
        return OUTPUT_PATH
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise


if __name__ == "__main__":
    download_weights()
