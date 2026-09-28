import math

import pytest

from ai_engine.clustering import cluster_coordinates
from ai_engine.cluster_summary import summarize_cluster


def test_dbscan_groups_five_points_inside_fifty_meters():
    origin = (19.0760, 72.8777)
    points = [
        origin,
        (origin[0] + 0.00008, origin[1]),
        (origin[0] - 0.00008, origin[1]),
        (origin[0], origin[1] + 0.00008),
        (origin[0], origin[1] - 0.00008),
    ]
    assert cluster_coordinates(points) == [0, 0, 0, 0, 0]


def test_dbscan_marks_isolated_point_as_noise():
    assert cluster_coordinates([(19.076, 72.8777), (19.08, 72.88)]) == [-1, -1]


@pytest.mark.parametrize("points", [[(91, 0)], [(0, 181)], [(math.nan, 0)]])
def test_dbscan_rejects_invalid_coordinates(points):
    with pytest.raises(ValueError):
        cluster_coordinates(points)


def test_cluster_summary_reports_centroid_category_and_risk():
    reports = [
        {"latitude": 19.0, "longitude": 72.0, "severity_score": 90, "category": "Pothole"},
        {"latitude": 19.0002, "longitude": 72.0002, "severity_score": 70, "category": "Pothole"},
        {"latitude": 19.0001, "longitude": 72.0001, "severity_score": 60, "category": "Crack"},
    ]
    summary = summarize_cluster(2, reports)
    assert summary == {
        "cluster_id": 2,
        "latitude": pytest.approx(19.0001),
        "longitude": pytest.approx(72.0001),
        "complaint_count": 3,
        "avg_severity": 73.33,
        "dominant_category": "Pothole",
        "risk_level": "HIGH_RISK_ZONE",
    }


def test_cluster_summary_uses_strict_greater_than_sixty_threshold():
    reports = [{"latitude": 1, "longitude": 2, "severity_score": 60, "category": "Pothole"}]
    assert summarize_cluster(0, reports)["risk_level"] == "STANDARD_RISK_ZONE"
