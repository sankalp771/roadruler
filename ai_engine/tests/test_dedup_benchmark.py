import csv
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

from ai_engine.benchmarks.test_dedup import calculate_metrics, load_manifest, validate_class_counts


def test_calculate_metrics_counts_false_positives_and_negatives():
    result = calculate_metrics(
        labels=[True, True, False, False],
        similarities=[0.9, 0.7, 0.8, 0.4],
        threshold=0.75,
    )

    assert result == {
        "true_positive": 1,
        "false_positive": 1,
        "false_negative": 1,
        "precision": 0.5,
        "recall": 0.5,
        "f1": 0.5,
    }


def test_manifest_requires_exactly_fifty_pairs_per_class():
    validate_class_counts(50, 50)


def test_manifest_rejects_missing_ground_truth_pairs():
    with pytest.raises(ValueError, match="exactly 50"):
        validate_class_counts(0, 0)


def test_load_manifest_accepts_fifty_labeled_pairs_per_class():
    rows = [["image_a", "image_b", "is_duplicate"]]
    rows.extend([[f"dup-a-{i}.jpg", f"dup-b-{i}.jpg", "true"] for i in range(50)])
    rows.extend([[f"distinct-a-{i}.jpg", f"distinct-b-{i}.jpg", "false"] for i in range(50)])
    output = StringIO()
    csv.writer(output).writerows(rows)
    contents = output.getvalue()
    manifest_path = Path("pairs.csv")

    with patch.object(Path, "is_file", return_value=True), patch.object(
        Path, "open", autospec=True, side_effect=lambda *_args, **_kwargs: StringIO(contents)
    ):
        pairs = load_manifest(manifest_path)

    assert len(pairs) == 100
    assert sum(is_duplicate for _, _, is_duplicate in pairs) == 50
