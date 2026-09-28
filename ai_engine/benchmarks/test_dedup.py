"""Evaluate visual deduplication against a labeled CSV of image pairs.

The manifest must contain exactly 50 positive and 50 negative pairs. This
module deliberately does not generate pairs or labels from the images.
"""

import argparse
import csv
import hashlib
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ai_engine.deduplication import compute_cosine_similarity  # noqa: E402

THRESHOLDS = (0.75, 0.78, 0.80, 0.82, 0.85, 0.88, 0.90)
TRUE_VALUES = {"1", "true", "duplicate", "yes"}
FALSE_VALUES = {"0", "false", "distinct", "no"}


def calculate_metrics(labels: list[bool], similarities: list[float], threshold: float) -> dict[str, float | int]:
    """Calculate binary duplicate-detection precision, recall, and F1."""
    if len(labels) != len(similarities):
        raise ValueError("labels and similarities must contain the same number of pairs")
    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be between 0 and 1")

    true_positive = false_positive = false_negative = 0
    for label, similarity in zip(labels, similarities):
        predicted = similarity >= threshold
        true_positive += int(label and predicted)
        false_positive += int(not label and predicted)
        false_negative += int(label and not predicted)

    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def validate_class_counts(duplicate_count: int, distinct_count: int) -> None:
    if (duplicate_count, distinct_count) != (50, 50):
        raise ValueError(
            f"Manifest needs exactly 50 duplicate and 50 distinct pairs; got {duplicate_count} and {distinct_count}"
        )


def load_manifest(manifest_path: Path) -> list[tuple[Path, Path, bool]]:
    """Load and validate exactly 50 duplicate and 50 distinct labeled pairs."""
    pairs: list[tuple[Path, Path, bool]] = []
    with manifest_path.open("r", newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        required = {"image_a", "image_b", "is_duplicate"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("CSV header must contain image_a,image_b,is_duplicate")
        for line_number, row in enumerate(reader, start=2):
            first_value = (row.get("image_a") or "").strip()
            second_value = (row.get("image_b") or "").strip()
            label_value = (row.get("is_duplicate") or "").strip().lower()
            if not first_value or not second_value or label_value not in TRUE_VALUES | FALSE_VALUES:
                raise ValueError(f"Invalid image pair or label on CSV line {line_number}")
            first_path = (manifest_path.parent / first_value).resolve()
            second_path = (manifest_path.parent / second_value).resolve()
            if not first_path.is_file() or not second_path.is_file():
                raise FileNotFoundError(f"Image path missing on CSV line {line_number}")
            pairs.append((first_path, second_path, label_value in TRUE_VALUES))

    duplicate_count = sum(label for _, _, label in pairs)
    distinct_count = len(pairs) - duplicate_count
    validate_class_counts(duplicate_count, distinct_count)
    return pairs


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def benchmark(manifest_path: Path) -> list[dict[str, Any]]:
    """Extract image embeddings, evaluate all labeled pairs, and return results."""
    from ai_engine.embeddings import extract_embedding

    pairs = load_manifest(manifest_path)
    hashes: dict[Path, str] = {}
    embeddings: dict[Path, Any] = {}
    labels: list[bool] = []
    similarities: list[float] = []

    for image_a, image_b, is_duplicate in pairs:
        for image_path in (image_a, image_b):
            if image_path not in embeddings:
                hashes[image_path] = _sha256(image_path)
                embeddings[image_path] = extract_embedding(str(image_path))
        if is_duplicate and hashes[image_a] == hashes[image_b]:
            raise ValueError(f"Positive pair uses byte-identical images: {image_a} and {image_b}")
        labels.append(is_duplicate)
        similarities.append(compute_cosine_similarity(embeddings[image_a], embeddings[image_b]))

    return [
        {"threshold": threshold, **calculate_metrics(labels, similarities, threshold)}
        for threshold in THRESHOLDS
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="CSV with 50 duplicate and 50 distinct image pairs")
    args = parser.parse_args()
    try:
        results = benchmark(args.manifest.resolve())
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"Benchmark could not run: {exc}", file=sys.stderr)
        return 2

    print("threshold,precision,recall,f1,tp,fp,fn")
    for result in results:
        print(
            f"{result['threshold']:.2f},{result['precision']:.4f},{result['recall']:.4f},"
            f"{result['f1']:.4f},{result['true_positive']},{result['false_positive']},{result['false_negative']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
