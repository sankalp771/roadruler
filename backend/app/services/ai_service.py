"""
AI Service Bridge (Day 5).
Connects the FastAPI backend to the ai_engine package (YOLOv8 inference +
severity scoring) so complaint records are enriched with automated
damage classification and severity grades.
"""

import logging
import sys
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

# ai_engine lives at the repo root, one level above backend/ — make it importable
# regardless of which directory uvicorn / celery was launched from.
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

PREFERRED_WEIGHTS_PATH = REPO_ROOT / "ai_engine" / "weights" / "pretrained_pothole.pt"
DEFAULT_WEIGHTS_PATH = REPO_ROOT / "ai_engine" / "weights" / "best.pt"

_detector = None
_detector_lock = threading.Lock()


def _resolve_weights_path() -> str:
    if settings.AI_WEIGHTS_PATH:
        return settings.AI_WEIGHTS_PATH
    if PREFERRED_WEIGHTS_PATH.exists():
        return str(PREFERRED_WEIGHTS_PATH)
    return str(DEFAULT_WEIGHTS_PATH)


def get_detector():
    """
    Lazily load the YOLOv8 detector exactly once per process.
    Model loading takes seconds, so it must never happen per-request;
    lazy (instead of import-time) loading keeps API startup fast and lets
    non-AI routes work even if AI dependencies are broken.
    """
    global _detector
    if _detector is None:
        with _detector_lock:
            if _detector is None:
                from ai_engine.inference import RoadDamageDetector

                weights_path = _resolve_weights_path()
                if not Path(weights_path).exists():
                    raise FileNotFoundError(
                        f"YOLO weights not found at '{weights_path}'. "
                        "Run ai_engine/scripts/download_pothole_weights.py first."
                    )
                logger.info(f"Initializing RoadDamageDetector with weights: {weights_path}")
                _detector = RoadDamageDetector(weights_path=weights_path)
    return _detector


def _normalize_detections(detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Some pre-trained weights expose numeric class names (e.g. {0: '0'}),
    which would break severity weighting and produce useless categories.
    Map any unrecognized class name back to the canonical RDD2022 name
    via the class_id so severity.py applies the correct weight.
    """
    from ai_engine.inference import CLASS_MAPPING
    from ai_engine.severity import CLASS_SEVERITY_WEIGHTS

    known_names = {name.lower() for name in CLASS_SEVERITY_WEIGHTS}
    normalized = []
    for det in detections:
        det = dict(det)
        name = str(det.get("class_name", ""))
        if name.lower() not in known_names:
            det["class_name"] = CLASS_MAPPING.get(det.get("class_id"), name)
        normalized.append(det)
    return normalized


def _pick_primary_category(detections: List[Dict[str, Any]]) -> Optional[str]:
    """Highest-confidence detection determines the AI-assigned category."""
    if not detections:
        return None
    primary = max(detections, key=lambda d: d.get("confidence", 0.0))
    return primary.get("class_name")


def analyze_image(image_bytes: bytes) -> Dict[str, Any]:
    """
    Full AI enrichment pipeline: bytes -> YOLO detections -> severity maths.

    Returns:
        dict with keys:
          - ai_category (str | None): e.g. "Pothole", None if nothing detected
          - severity_score (float): 0-100
          - severity_level (str): CRITICAL / MODERATE / MINOR
          - detections_count (int)
    """
    if not image_bytes:
        raise ValueError("analyze_image received empty image bytes")

    from ai_engine.severity import calculate_severity

    detector = get_detector()
    detections = _normalize_detections(detector.predict(image_bytes))
    severity = calculate_severity(detections)

    result = {
        "ai_category": _pick_primary_category(detections),
        "severity_score": severity["severity_score"],
        "severity_level": severity["severity_level"],
        "detections_count": len(detections),
        "detection_details": [
            {
                "class_id": int(detection.get("class_id", -1)),
                "class_name": str(detection.get("class_name", "Unknown")),
                "confidence": float(detection.get("confidence", 0.0)),
                "bbox_normalized": detection.get("bbox_normalized"),
            }
            for detection in detections
        ],
    }
    logger.info(
        "AI analysis complete: category=%s score=%s level=%s detections=%d",
        result["ai_category"],
        result["severity_score"],
        result["severity_level"],
        result["detections_count"],
    )
    return result
