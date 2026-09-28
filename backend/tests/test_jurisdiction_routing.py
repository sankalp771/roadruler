from types import SimpleNamespace
from unittest.mock import MagicMock

from app.services.jurisdiction_routing import resolve_jurisdiction


def test_resolve_jurisdiction_returns_selected_boundary_and_department():
    boundary = SimpleNamespace(id="WARD_3", department_name="Ward Local Maintenance")
    db = MagicMock()
    db.query.return_value.filter.return_value.order_by.return_value.first.return_value = boundary

    result = resolve_jurisdiction(db, longitude=72.87, latitude=19.21)

    assert result == ("WARD_3", "Ward Local Maintenance")


def test_resolve_jurisdiction_leaves_uncovered_point_unassigned():
    db = MagicMock()
    db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None

    assert resolve_jurisdiction(db, longitude=72.87, latitude=19.21) == (None, None)
