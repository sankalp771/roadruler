"""Spatial candidate filtering and visual similarity matching helpers."""

from collections.abc import Iterable, Mapping
from typing import Any

import numpy as np


def compute_cosine_similarity(vec1: Any, vec2: Any) -> float:
    """Return cosine similarity for two finite, non-empty one-dimensional vectors."""
    first = np.asarray(vec1, dtype=np.float64)
    second = np.asarray(vec2, dtype=np.float64)
    if first.ndim != 1 or second.ndim != 1 or first.size == 0 or second.size == 0:
        raise ValueError("Embeddings must be non-empty one-dimensional vectors")
    if first.shape != second.shape:
        raise ValueError("Embeddings must have the same dimensions")
    if not np.isfinite(first).all() or not np.isfinite(second).all():
        raise ValueError("Embeddings must contain only finite values")

    denominator = float(np.linalg.norm(first) * np.linalg.norm(second))
    if denominator == 0:
        return 0.0
    return float(np.clip(np.dot(first, second) / denominator, -1.0, 1.0))


def check_duplicate(
    new_embedding: Any,
    candidate_embeddings: Iterable[tuple[str, Any] | Mapping[str, Any]],
    threshold: float = 0.82,
) -> tuple[bool, str | None, float]:
    """Return whether the best candidate meets threshold, its ID, and similarity.

    Candidates are ``(complaint_id, embedding)`` pairs or mappings containing
    ``id`` and ``embedding`` keys. Spatial filtering belongs to the caller so
    this function can also be used with pre-filtered offline datasets.
    """
    if not np.isfinite(threshold) or not -1 <= threshold <= 1:
        raise ValueError("threshold must be a finite cosine similarity in [-1, 1]")

    best_id: str | None = None
    best_similarity = 0.0
    for candidate in candidate_embeddings:
        if isinstance(candidate, Mapping):
            candidate_id = candidate.get("id")
            embedding = candidate.get("embedding")
        else:
            try:
                candidate_id, embedding = candidate
            except (TypeError, ValueError) as exc:
                raise ValueError("Each candidate must contain an ID and embedding") from exc
        if candidate_id is None or embedding is None:
            continue
        similarity = compute_cosine_similarity(new_embedding, embedding)
        if similarity > best_similarity:
            best_id = str(candidate_id)
            best_similarity = similarity

    return best_similarity >= threshold and best_id is not None, best_id, best_similarity
