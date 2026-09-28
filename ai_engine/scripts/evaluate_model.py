"""Create honest binary road-damage evaluation charts from a labeled CSV."""
import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix, precision_recall_curve


def load_labels(manifest: Path) -> tuple[list[int], list[float]]:
    with manifest.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        required = {"ground_truth", "confidence"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("CSV must include ground_truth and confidence columns")
        labels: list[int] = []
        scores: list[float] = []
        for line_number, row in enumerate(reader, start=2):
            try:
                label = int(row["ground_truth"])
                score = float(row["confidence"])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid label or confidence on CSV line {line_number}") from exc
            if label not in (0, 1) or not 0 <= score <= 1:
                raise ValueError(f"Expected binary labels and confidence in [0, 1] on CSV line {line_number}")
            labels.append(label)
            scores.append(score)
    if not labels:
        raise ValueError("CSV must contain at least one labeled example")
    if set(labels) != {0, 1}:
        raise ValueError("CSV must contain both positive and negative ground-truth examples")
    return labels, scores


def export_charts(labels: list[int], scores: list[float], output_dir: Path, threshold: float = 0.5) -> tuple[Path, Path]:
    if len(labels) != len(scores) or not labels:
        raise ValueError("Labels and confidence scores must be non-empty and have equal lengths")
    if set(labels) != {0, 1}:
        raise ValueError("Evaluation data must contain both classes")
    if any(label not in (0, 1) for label in labels) or any(not 0 <= score <= 1 for score in scores):
        raise ValueError("Expected binary labels and confidence scores in [0, 1]")
    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be in [0, 1]")

    output_dir.mkdir(parents=True, exist_ok=True)
    precision, recall, _ = precision_recall_curve(labels, scores)
    pr_path = output_dir / "precision_recall_curve.png"
    fig, axis = plt.subplots(figsize=(7, 5))
    axis.step(recall, precision, where="post", color="#2563eb")
    axis.set(xlabel="Recall", ylabel="Precision", title="Road-damage precision-recall curve", xlim=(0, 1), ylim=(0, 1.05))
    axis.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(pr_path, dpi=160)
    plt.close(fig)

    predictions = [int(score >= threshold) for score in scores]
    matrix = confusion_matrix(labels, predictions, labels=[0, 1])
    cm_path = output_dir / "confusion_matrix.png"
    fig, axis = plt.subplots(figsize=(6, 5))
    ConfusionMatrixDisplay(matrix, display_labels=["No damage", "Damage"]).plot(ax=axis, cmap="Blues", colorbar=False)
    axis.set_title(f"Confusion matrix (confidence threshold {threshold:.2f})")
    fig.tight_layout()
    fig.savefig(cm_path, dpi=160)
    plt.close(fig)
    return pr_path, cm_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="CSV with independently labeled ground_truth (0/1) and confidence (0..1)")
    parser.add_argument("--output-dir", type=Path, default=Path("docs/deliverables/centraltasks/metrics"))
    parser.add_argument("--threshold", type=float, default=0.5)
    args = parser.parse_args()
    labels, scores = load_labels(args.manifest)
    for path in export_charts(labels, scores, args.output_dir, args.threshold):
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
