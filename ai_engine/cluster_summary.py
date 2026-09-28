from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any


def summarize_cluster(cluster_id: int, complaints: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize cluster center, severity, and most frequent hazard category."""
    if not complaints:
        raise ValueError("complaints must contain at least one cluster member")
    latitudes = [float(item["latitude"]) for item in complaints]
    longitudes = [float(item["longitude"]) for item in complaints]
    severities = [float(item.get("severity_score") or 0) for item in complaints]
    if any(not 0 <= value <= 100 for value in severities):
        raise ValueError("severity_score must be between 0 and 100")
    categories = [str(item.get("category") or "UNKNOWN") for item in complaints]
    counts = Counter(categories)
    dominant = sorted(counts, key=lambda category: (-counts[category], category))[0]
    average = sum(severities) / len(severities)
    return {
        "cluster_id": int(cluster_id),
        "latitude": sum(latitudes) / len(latitudes),
        "longitude": sum(longitudes) / len(longitudes),
        "complaint_count": len(complaints),
        "avg_severity": round(average, 2),
        "dominant_category": dominant,
        "risk_level": "HIGH_RISK_ZONE" if average > 60 else "STANDARD_RISK_ZONE",
    }
