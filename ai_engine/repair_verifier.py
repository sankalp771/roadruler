"""Conservative before/after repair verification using detections and embeddings."""

from pathlib import Path
import sys
from typing import Any, Callable, Dict, List, Optional, Sequence

import numpy as np

Detection = Dict[str, Any]


def _normalized_box(detection: Detection) -> Sequence[float]:
    box = detection.get("bbox_normalized")
    if not isinstance(box, (list, tuple)) or len(box) != 4:
        raise ValueError("Damage detections must include four normalized box coordinates")
    x1, y1, x2, y2 = (float(value) for value in box)
    if not (0 <= x1 < x2 <= 1 and 0 <= y1 < y2 <= 1):
        raise ValueError("Damage detection box coordinates must be normalized to [0, 1]")
    return x1, y1, x2, y2


def _overlap_fraction(original_box: Sequence[float], later_box: Sequence[float]) -> float:
    x1 = max(original_box[0], later_box[0])
    y1 = max(original_box[1], later_box[1])
    x2 = min(original_box[2], later_box[2])
    y2 = min(original_box[3], later_box[3])
    intersection = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    original_area = (original_box[2] - original_box[0]) * (original_box[3] - original_box[1])
    return intersection / original_area


def _cosine_similarity(first: Sequence[float], second: Sequence[float]) -> float:
    first_vector = np.asarray(first, dtype=np.float64).reshape(-1)
    second_vector = np.asarray(second, dtype=np.float64).reshape(-1)
    if first_vector.size == 0 or first_vector.shape != second_vector.shape:
        raise ValueError("Before and after embeddings must be non-empty vectors of equal size")
    denominator = float(np.linalg.norm(first_vector) * np.linalg.norm(second_vector))
    if denominator == 0:
        return 0.0
    return float(np.dot(first_vector, second_vector) / denominator)


def verify_repair(
    before_image: bytes,
    after_image: bytes,
    *,
    detector: Optional[Callable[[bytes], List[Detection]]] = None,
    embedder: Optional[Callable[[bytes], Sequence[float]]] = None,
    similarity_threshold: float = 0.80,
    overlap_threshold: float = 0.10,
) -> Dict[str, Any]:
    """Verify a repair only when damage disappears and the scene still matches.

    Detector/embedder injection keeps the decision logic testable; production
    defaults reuse RoadRuler's shared YOLO and ResNet50 pipelines.
    """
    if not before_image or not after_image:
        raise ValueError("Both before and after images are required")
    if not 0.0 <= similarity_threshold <= 1.0:
        raise ValueError("similarity_threshold must be between 0 and 1")
    if not 0.0 <= overlap_threshold <= 1.0:
        raise ValueError("overlap_threshold must be between 0 and 1")

    if detector is None:
        backend_root = str(Path(__file__).resolve().parents[1] / "backend")
        if backend_root not in sys.path:
            sys.path.insert(0, backend_root)
        from app.services.ai_service import get_detector

        detector = get_detector().predict
    if embedder is None:
        from ai_engine.embeddings import extract_embedding

        embedder = extract_embedding

    original_detections = detector(before_image)
    after_detections = detector(after_image)
    if not original_detections:
        return {"status": "NEEDS_REVIEW", "reason": "ORIGINAL_DAMAGE_NOT_DETECTED", "similarity": None}

    original_boxes = [_normalized_box(detection) for detection in original_detections]
    later_boxes = [_normalized_box(detection) for detection in after_detections]
    remaining_in_original_area = [
        later for later in later_boxes
        if any(_overlap_fraction(original, later) >= overlap_threshold for original in original_boxes)
    ]
    if remaining_in_original_area:
        return {
            "status": "REPAIR_NOT_VERIFIED",
            "reason": "DAMAGE_REMAINS_IN_ORIGINAL_AREA",
            "similarity": None,
            "remaining_damage_count": len(remaining_in_original_area),
        }

    similarity = _cosine_similarity(embedder(before_image), embedder(after_image))
    if not np.isfinite(similarity) or similarity < similarity_threshold:
        return {
            "status": "NEEDS_REVIEW",
            "reason": "SCENE_SIMILARITY_TOO_LOW",
            "similarity": round(similarity, 4),
            "remaining_damage_count": 0,
        }
    return {
        "status": "REPAIR_VERIFIED",
        "reason": "DAMAGE_CLEARED_AND_SCENE_MATCHED",
        "similarity": round(similarity, 4),
        "remaining_damage_count": 0,
    }
