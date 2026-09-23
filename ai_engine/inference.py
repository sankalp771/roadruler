"""
YOLOv8 Inference Engine for Road Damage Detection.
Provides object detection wrapper for road damage categories (potholes, cracks, waterlogging).
"""

import argparse
import io
import json
import logging
import os
from typing import Any, Dict, List, Union

import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# RDD2022 standard class map with fallback for generic YOLO models
CLASS_MAPPING: Dict[int, str] = {
    0: "Pothole",
    1: "Longitudinal Crack",
    2: "Transverse Crack",
    3: "Alligator Crack",
    4: "Waterlogging",
}


class RoadDamageDetector:
    """YOLOv8 Object Detection Wrapper for Road Damage Identification."""

    def __init__(self, weights_path: str = "yolov8n.pt"):
        """
        Initialize the Road Damage Detector with model weights.

        Args:
            weights_path (str): Path to trained PyTorch (.pt) weights file or pre-trained model name.
        """
        self.weights_path = weights_path
        logger.info(f"Loading YOLOv8 model from {self.weights_path}...")
        try:
            self.model = YOLO(self.weights_path)
            logger.info("YOLOv8 model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load YOLO model weights from {self.weights_path}: {str(e)}")
            raise RuntimeError(f"Model initialization error: {str(e)}") from e

    def _preprocess_input(self, image_input: Union[str, bytes, np.ndarray, Image.Image]) -> np.ndarray:
        """
        Preprocess various image input formats into OpenCV BGR numpy array.

        Args:
            image_input: File path (str), raw image bytes (bytes), PIL Image, or numpy array.

        Returns:
            np.ndarray: OpenCV BGR image matrix.
        """
        if isinstance(image_input, str):
            if not os.path.exists(image_input):
                raise FileNotFoundError(f"Image file not found: {image_input}")
            img = cv2.imread(image_input)
            if img is None:
                raise ValueError(f"Failed to read image at path: {image_input}")
            return img
        elif isinstance(image_input, bytes):
            image = Image.open(io.BytesIO(image_input))
            return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        elif isinstance(image_input, Image.Image):
            return cv2.cvtColor(np.array(image_input), cv2.COLOR_RGB2BGR)
        elif isinstance(image_input, np.ndarray):
            return image_input
        else:
            raise TypeError(f"Unsupported image input type: {type(image_input)}")

    def predict(
        self,
        image_input: Union[str, bytes, np.ndarray, Image.Image],
        conf_threshold: float = 0.25,
    ) -> List[Dict[str, Any]]:
        """
        Run inference on an image and return structured damage detections.

        Args:
            image_input: Input image in supported format.
            conf_threshold (float): Confidence threshold for bounding box filtering.

        Returns:
            List[Dict[str, Any]]: List of parsed detection dicts containing bounding box, class, and confidence.
        """
        image_bgr = self._preprocess_input(image_input)
        img_h, img_w = image_bgr.shape[:2]

        results = self.model(image_bgr, conf=conf_threshold, verbose=False)

        parsed_detections: List[Dict[str, Any]] = []

        for result in results:
            boxes = result.boxes
            if boxes is None or len(boxes) == 0:
                continue

            for box in boxes:
                x1, y1, x2, y2 = map(float, box.xyxy[0].tolist())
                confidence = float(box.conf[0].item())
                class_id = int(box.cls[0].item())

                # Map class ID using predefined map or model's internal names
                if hasattr(self.model, "names") and class_id in self.model.names:
                    class_name = self.model.names[class_id]
                else:
                    class_name = CLASS_MAPPING.get(class_id, f"damage_class_{class_id}")

                norm_x1 = round(x1 / img_w, 4)
                norm_y1 = round(y1 / img_h, 4)
                norm_x2 = round(x2 / img_w, 4)
                norm_y2 = round(y2 / img_h, 4)

                parsed_detections.append(
                    {
                        "class_id": class_id,
                        "class_name": class_name,
                        "confidence": round(confidence, 4),
                        "bbox": [round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)],
                        "bbox_normalized": [norm_x1, norm_y1, norm_x2, norm_y2],
                        "area_pixels": round((x2 - x1) * (y2 - y1), 2),
                    }
                )

        logger.info(f"Inference complete. Detected {len(parsed_detections)} damage regions.")
        return parsed_detections


def main():
    parser = argparse.ArgumentParser(description="Road Damage Detector YOLOv8 CLI")
    parser.add_argument("--image", type=str, required=True, help="Path to input road image")
    parser.add_argument("--weights", type=str, default="yolov8n.pt", help="Path to YOLO weights file")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold")

    args = parser.parse_args()

    detector = RoadDamageDetector(weights_path=args.weights)
    detections = detector.predict(args.image, conf_threshold=args.conf)

    print("\n--- Detections Output ---")
    print(json.dumps(detections, indent=2))


if __name__ == "__main__":
    main()
