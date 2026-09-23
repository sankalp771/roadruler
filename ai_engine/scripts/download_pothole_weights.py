"""Download the RDD-trained YOLOv8s road-damage model used by RoadRuler."""

import logging
import urllib.request
import zipfile
from pathlib import Path


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
WEIGHTS_URL = (
    "https://huggingface.co/vinothvikas1987/pothole-detection-yolov8/"
    "resolve/main/best.pt"
)
OUTPUT_PATH = REPO_ROOT / "ai_engine" / "weights" / "road_damage_v8s.pt"


def download_weights() -> Path:
    """Download atomically and validate the checkpoint container before use."""
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = OUTPUT_PATH.with_suffix(".pt.download")
    logger.info("Downloading road-damage weights from %s", WEIGHTS_URL)

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

        temporary_path.replace(OUTPUT_PATH)
        logger.info("Road-damage weights saved to %s", OUTPUT_PATH)
        return OUTPUT_PATH
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise


if __name__ == "__main__":
    download_weights()
