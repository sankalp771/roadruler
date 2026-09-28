from collections.abc import Sequence
import math

import numpy as np
from sklearn.cluster import DBSCAN

EARTH_RADIUS_METERS = 6_371_008.8


def cluster_coordinates(
    coordinates: Sequence[tuple[float, float]],
    *,
    eps_meters: float = 50.0,
    min_samples: int = 3,
) -> list[int]:
    """Cluster ``(latitude, longitude)`` points using a haversine radius."""
    if not math.isfinite(eps_meters) or eps_meters <= 0:
        raise ValueError("eps_meters must be a positive finite number")
    if min_samples < 1:
        raise ValueError("min_samples must be at least 1")
    if not coordinates:
        return []

    points = np.asarray(coordinates, dtype=float)
    if points.ndim != 2 or points.shape[1] != 2 or not np.isfinite(points).all():
        raise ValueError("coordinates must contain finite latitude/longitude pairs")
    if (np.abs(points[:, 0]) > 90).any() or (np.abs(points[:, 1]) > 180).any():
        raise ValueError("latitude/longitude are outside valid ranges")

    model = DBSCAN(
        eps=eps_meters / EARTH_RADIUS_METERS,
        min_samples=min_samples,
        metric="haversine",
        algorithm="ball_tree",
    )
    return model.fit_predict(np.radians(points)).astype(int).tolist()
