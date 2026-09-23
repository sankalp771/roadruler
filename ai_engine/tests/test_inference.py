"""
Test Suite for YOLOv8 Road Damage Detector Inference Engine.
"""

import os
import unittest
import cv2
import numpy as np
from ai_engine.inference import RoadDamageDetector


class TestRoadDamageDetector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_image_path = "test_road.jpg"
        # Generate a synthetic test road image (640x640 RGB)
        img = np.zeros((640, 640, 3), dtype=np.uint8)
        img[:] = (80, 80, 80)  # Asphalt gray
        # Add road lane markings
        cv2.line(img, (320, 0), (320, 640), (255, 255, 255), 4)
        # Add synthetic dark pothole ellipse
        cv2.ellipse(img, (200, 300), (50, 30), 0, 0, 360, (30, 30, 30), -1)
        cv2.imwrite(cls.test_image_path, img)

        cls.detector = RoadDamageDetector(weights_path="yolov8n.pt")

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_image_path):
            os.remove(cls.test_image_path)

    def test_predict_with_filepath(self):
        detections = self.detector.predict(self.test_image_path, conf_threshold=0.10)
        self.assertIsInstance(detections, list)
        print(f"\n[Test Filepath] Detections count: {len(detections)}")

    def test_predict_with_bytes(self):
        with open(self.test_image_path, "rb") as f:
            image_bytes = f.read()
        detections = self.detector.predict(image_bytes, conf_threshold=0.10)
        self.assertIsInstance(detections, list)
        print(f"[Test Bytes] Detections count: {len(detections)}")


if __name__ == "__main__":
    unittest.main()
