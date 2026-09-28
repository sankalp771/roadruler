"""
Unit Test Suite for train.py Model Training Pipeline.
"""

import os
import shutil
import unittest
from ai_engine.train import train


class TestTrainPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_yaml = "ai_engine/data/road_damage.yaml"
        cls.weights_dir = "ai_engine/weights"
        
        # Verify base dataset config exists, otherwise skip
        if not os.path.exists(cls.test_yaml):
            # Create a mock base dataset layout so test can run independently
            from ai_engine.scripts.prepare_rdd import generate_synthetic_raw_dataset, process_dataset, create_dataset_config_yaml
            generate_synthetic_raw_dataset("ai_engine/data/raw", num_samples=15)
            process_dataset("ai_engine/data/raw", "ai_engine/data")
            create_dataset_config_yaml(cls.test_yaml, "ai_engine/data")

    def test_training_pipeline_execution(self):
        # Run 2 epochs on the quick subset
        # This executes real backpropagation and PyTorch parameters updates on CPU
        train(
            data_yaml=self.test_yaml,
            epochs=2,
            batch_size=2,
            imgsz=64,  # Use small image size to make it extremely rapid
            quick=True
        )
        
        # Verify weights and metrics results are generated
        self.assertTrue(os.path.exists(os.path.join(self.weights_dir, "best.pt")))
        self.assertTrue(os.path.exists(os.path.join(self.weights_dir, "results.csv")))

    @classmethod
    def tearDownClass(cls):
        # Clean up generated runs folder created by ultralytics
        if os.path.exists("runs"):
            shutil.rmtree("runs")


if __name__ == "__main__":
    unittest.main()
