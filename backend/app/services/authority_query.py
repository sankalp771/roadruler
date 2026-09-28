from datetime import timedelta
from typing import Optional

from sqlalchemy import and_, case, func, or_
from sqlalchemy.sql.elements import ColumnElement

from app.models.complaint import Complaint


def build_complaint_filters(
    *,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    ward_id: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    sla_state: Optional[str] = None,
) -> ColumnElement[bool]:
    """Build parameterized authority filters with active-only default scope."""
    filters = []
    if status:
        filters.append(func.upper(Complaint.status) == status.upper())
    else:
        filters.append(Complaint.status.notin_(("RESOLVED", "CANCELLED")))
    if severity:
        filters.append(func.upper(Complaint.severity_level) == severity.upper())
    if ward_id:
        filters.append(Complaint.ward_id == ward_id)
    if category:
        filters.append(
            or_(
                func.upper(Complaint.category) == category.upper(),
                func.upper(Complaint.ai_category) == category.upper(),
            )
        )
    if search:
        escaped = search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        pattern = f"%{escaped}%"
        filters.append(
            or_(
                Complaint.id.ilike(pattern, escape="\\"),
                Complaint.category.ilike(pattern, escape="\\"),
                Complaint.ai_category.ilike(pattern, escape="\\"),
                Complaint.description.ilike(pattern, escape="\\"),
            )
        )
    if sla_state:
        severity_level = func.upper(Complaint.severity_level)
        filters.append(severity_level.in_(("CRITICAL", "MODERATE", "MINOR")))
        sla_duration = case(
            (severity_level == "CRITICAL", timedelta(hours=48)),
            (severity_level == "MODERATE", timedelta(days=7)),
            else_=timedelta(days=30),
        )
        deadline_passed = Complaint.created_at < func.now() - sla_duration
        filters.append(deadline_passed if sla_state == "OVERDUE" else ~deadline_passed)
    return and_(*filters)
