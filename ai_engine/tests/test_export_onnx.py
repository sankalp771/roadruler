from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from ai_engine.scripts.export_onnx import benchmark_cpu, export_model


def test_export_onnx_rejects_missing_checkpoint(tmp_path: Path):
    with pytest.raises(FileNotFoundError, match="YOLO weights not found"):
        export_model(tmp_path / "missing.pt", tmp_path / "onnx")


def test_export_onnx_copies_ultralytics_artifact_to_output_directory(tmp_path: Path):
    weights = tmp_path / "model.pt"
    weights.write_bytes(b"weights")
    exported = tmp_path / "ultralytics" / "model.onnx"
    exported.parent.mkdir()
    exported.write_bytes(b"onnx")
    model = Mock()
    model.export.return_value = str(exported)
    with patch("ai_engine.scripts.export_onnx.YOLO", return_value=model):
        result = export_model(weights, tmp_path / "output")
    assert result.read_bytes() == b"onnx"
    model.export.assert_called_once_with(format="onnx", imgsz=640, device="cpu", dynamic=False, simplify=False, opset=17)


def test_cpu_benchmark_runs_warmups_and_returns_median_latency():
    detector = Mock()
    with patch("ai_engine.scripts.export_onnx.time.perf_counter", side_effect=[0, 0.010, 1, 1.020, 2, 2.030]):
        result = benchmark_cpu(detector, "frame", warmup=1, runs=3)
    assert result == pytest.approx(20.0)
    assert detector.predict.call_count == 4
