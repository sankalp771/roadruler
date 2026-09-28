"""
Unit Test Suite for prepare_rdd.py Dataset Curation Engine.
"""

import os
import shutil
import unittest
from ai_engine.scripts.prepare_rdd import (
    generate_synthetic_raw_dataset,
    process_dataset,
    create_dataset_config_yaml,
)


class TestPrepareRDD(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_raw_dir = "ai_engine/data/test_raw"
        cls.test_output_dir = "ai_engine/data/test_output"

    def test_end_to_end_preparation(self):
        # 1. Generate a small synthetic dataset of 15 samples
        generate_synthetic_raw_dataset(self.test_raw_dir, num_samples=15)
        
        # 2. Process dataset
        processed, errors = process_dataset(self.test_raw_dir, self.test_output_dir, val_split=0.2)
        
        self.assertEqual(processed, 15)
        self.assertEqual(errors, 0)
        
        # 3. Check folders existence
        for split in ["train", "val"]:
            self.assertTrue(os.path.exists(os.path.join(self.test_output_dir, "images", split)))
            self.assertTrue(os.path.exists(os.path.join(self.test_output_dir, "labels", split)))
            
        # 4. Check that labels are formatted correctly
        train_labels_dir = os.path.join(self.test_output_dir, "labels", "train")
        label_files = [f for f in os.listdir(train_labels_dir) if f.endswith(".txt")]
        self.assertTrue(len(label_files) > 0)
        
        # Read one file to verify YOLO formatting
        sample_file = os.path.join(train_labels_dir, label_files[0])
        with open(sample_file, "r") as f:
            lines = f.readlines()
            self.assertTrue(len(lines) > 0)
            for line in lines:
                parts = line.strip().split()
                self.assertEqual(len(parts), 5)
                class_id = int(parts[0])
                x, y, w, h = map(float, parts[1:])
                self.assertTrue(0 <= class_id <= 4)
                self.assertTrue(0.0 <= x <= 1.0)
                self.assertTrue(0.0 <= y <= 1.0)
                self.assertTrue(0.0 <= w <= 1.0)
                self.assertTrue(0.0 <= h <= 1.0)
                
        # 5. Create YAML config file check
        yaml_path = os.path.join(self.test_output_dir, "road_damage.yaml")
        create_dataset_config_yaml(yaml_path, self.test_output_dir)
        self.assertTrue(os.path.exists(yaml_path))

    @classmethod
    def tearDownClass(cls):
        # Clean up temporary folders
        for folder in [cls.test_raw_dir, cls.test_output_dir]:
            if os.path.exists(folder):
                shutil.rmtree(folder)


if __name__ == "__main__":
    unittest.main()
