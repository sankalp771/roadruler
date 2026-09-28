import csv
from pathlib import Path

import pytest

from ai_engine.scripts.evaluate_model import export_charts, load_labels


def test_evaluation_exports_both_charts_from_labeled_examples(tmp_path: Path):
    labels = [0, 0, 1, 1]
    scores = [0.1, 0.7, 0.6, 0.9]

    pr_path, cm_path = export_charts(labels, scores, tmp_path / "metrics")

    assert pr_path.is_file() and pr_path.stat().st_size > 0
    assert cm_path.is_file() and cm_path.stat().st_size > 0


def test_manifest_requires_both_ground_truth_classes(tmp_path: Path):
    manifest = tmp_path / "labels.csv"
    with manifest.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=["ground_truth", "confidence"])
        writer.writeheader()
        writer.writerows([{"ground_truth": 1, "confidence": 0.9}, {"ground_truth": 1, "confidence": 0.4}])

    with pytest.raises(ValueError, match="both positive and negative"):
        load_labels(manifest)
