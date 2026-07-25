"""
Script to download pre-trained YOLOv8 pothole weights from Hugging Face.
Ensures we have high-quality, real-world detection capability on CPU.
"""

import os
import urllib.request
import logging
import shutil

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

WEIGHTS_URL = "https://huggingface.co/peterhdd/pothole-detection-yolov8/resolve/main/best.pt"
OUTPUT_PATH = "ai_engine/weights/best.pt"


def download_weights():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    logger.info(f"Downloading pre-trained pothole weights from: {WEIGHTS_URL}...")
    
    try:
        req = urllib.request.Request(
            WEIGHTS_URL, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=30) as response, open(OUTPUT_PATH, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        logger.info(f"Weights downloaded successfully and saved to: {OUTPUT_PATH}")
    except Exception as e:
        logger.error(f"Failed to download pre-trained weights: {str(e)}")
        # Fallback to copy yolov8n.pt if download fails
        if os.path.exists("yolov8n.pt"):
            shutil.copy2("yolov8n.pt", OUTPUT_PATH)
            logger.info("Copied base yolov8n.pt as fallback weights.")
        else:
            raise e


if __name__ == "__main__":
    download_weights()
