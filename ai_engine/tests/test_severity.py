"""
Unit Test Suite for severity.py Damage Severity Calculator Engine.
"""

import unittest
from ai_engine.severity import calculate_severity


class TestSeverityCalculator(unittest.TestCase):
    def test_large_pothole_severity(self):
        # 25% frame area pothole
        detections = [
            {
                "class_id": 0,
                "class_name": "Pothole",
                "confidence": 0.90,
                "bbox": [100.0, 100.0, 420.0, 340.0],
                "bbox_normalized": [0.10, 0.15, 0.60, 0.65],  # w = 0.50, h = 0.50 -> area = 0.25
                "area_pixels": 76800.0,
            }
        ]
        
        result = calculate_severity(detections)
        self.assertEqual(result["severity_score"], 85.0)
        self.assertEqual(result["severity_level"], "CRITICAL")
        print(f"\n[Test Large Pothole] Score: {result['severity_score']}, Grade: {result['severity_level']}")

    def test_minor_longitudinal_crack(self):
        # 5% area longitudinal crack
        detections = [
            {
                "class_id": 1,
                "class_name": "Longitudinal Crack",
                "confidence": 0.85,
                "bbox": [50.0, 100.0, 150.0, 340.0],
                "bbox_normalized": [0.10, 0.20, 0.30, 0.45],  # w = 0.20, h = 0.25 -> area = 0.05
                "area_pixels": 24000.0,
            }
        ]
        
        result = calculate_severity(detections)
        # 0.05 * 100 * 0.4 * 3.4 = 6.8
        self.assertEqual(result["severity_score"], 6.8)
        self.assertEqual(result["severity_level"], "MINOR")
        print(f"[Test Minor Crack] Score: {result['severity_score']}, Grade: {result['severity_level']}")

    def test_empty_detections(self):
        result = calculate_severity([])
        self.assertEqual(result["severity_score"], 0.0)
        self.assertEqual(result["severity_level"], "MINOR")

    def test_invalid_input_fallback(self):
        # Missing required bbox key
        detections = [
            {
                "class_id": 0,
                "class_name": "Pothole",
                "confidence": 0.90,
                # missing bbox_normalized
            }
        ]
        result = calculate_severity(detections)
        self.assertEqual(result["severity_score"], 0.0)
        self.assertEqual(result["severity_level"], "MINOR")


if __name__ == "__main__":
    unittest.main()
