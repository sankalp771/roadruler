from unittest.mock import Mock, patch

import numpy as np

from ai_engine.inference import RoadDamageDetector


def test_onnx_checkpoint_uses_cpu_execution():
    model = Mock()
    model.names = {}
    model.return_value = []
    with patch("ai_engine.inference.YOLO", return_value=model):
        detector = RoadDamageDetector("model.onnx")
        detector.predict(np.zeros((16, 16, 3), dtype=np.uint8))
    assert model.call_args.kwargs["device"] == "cpu"


def test_pytorch_checkpoint_keeps_default_device_selection():
    model = Mock()
    model.names = {}
    model.return_value = []
    with patch("ai_engine.inference.YOLO", return_value=model):
        detector = RoadDamageDetector("model.pt")
        detector.predict(np.zeros((16, 16, 3), dtype=np.uint8))
    assert "device" not in model.call_args.kwargs
