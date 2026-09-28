"""
Test Suite for ResNet50 Visual Embedding Vector Generator.
"""

import os
import unittest
import cv2
import numpy as np
from PIL import Image
from ai_engine.embeddings import extract_embedding, get_extractor


class TestResNet50Embeddings(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_image_path = "test_emb_road.jpg"
        # Generate a synthetic test road image (300x300 RGB)
        img = np.zeros((300, 300, 3), dtype=np.uint8)
        img[:] = (100, 100, 100)  # Asphalt gray
        # Add some lane markings
        cv2.line(img, (150, 0), (150, 300), (255, 255, 255), 2)
        cv2.imwrite(cls.test_image_path, img)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_image_path):
            os.remove(cls.test_image_path)

    def test_singleton_extractor(self):
        extractor1 = get_extractor()
        extractor2 = get_extractor()
        self.assertIs(extractor1, extractor2)

    def test_extract_with_filepath(self):
        embedding = extract_embedding(self.test_image_path)
        self.assertIsInstance(embedding, np.ndarray)
        self.assertEqual(embedding.shape, (2048,))
        # Assert L2 norm is approximately 1.0
        norm = np.linalg.norm(embedding)
        self.assertAlmostEqual(norm, 1.0, places=5)

    def test_extract_with_bytes(self):
        with open(self.test_image_path, "rb") as f:
            image_bytes = f.read()
        embedding = extract_embedding(image_bytes)
        self.assertIsInstance(embedding, np.ndarray)
        self.assertEqual(embedding.shape, (2048,))
        norm = np.linalg.norm(embedding)
        self.assertAlmostEqual(norm, 1.0, places=5)

    def test_extract_with_ndarray(self):
        img_array = cv2.imread(self.test_image_path)
        embedding = extract_embedding(img_array)
        self.assertIsInstance(embedding, np.ndarray)
        self.assertEqual(embedding.shape, (2048,))
        norm = np.linalg.norm(embedding)
        self.assertAlmostEqual(norm, 1.0, places=5)

    def test_extract_with_pil(self):
        pil_img = Image.open(self.test_image_path)
        embedding = extract_embedding(pil_img)
        self.assertIsInstance(embedding, np.ndarray)
        self.assertEqual(embedding.shape, (2048,))
        norm = np.linalg.norm(embedding)
        self.assertAlmostEqual(norm, 1.0, places=5)


if __name__ == "__main__":
    unittest.main()
