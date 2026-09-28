import json
import logging
from datetime import datetime
from typing import Any

import redis
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.complaint import Complaint

logger = logging.getLogger(__name__)
router = APIRouter()
CACHE_KEY = "public:stats:v1"


class WardStats(BaseModel):
    ward_id: str
    department_name: str | None
    total_complaints: int
    resolved_complaints: int
    resolution_rate: float
    average_resolution_days: float | None


class PublicStats(BaseModel):
    generated_at: datetime
    total_complaints: int
    resolved_complaints: int
    resolution_rate: float
    average_resolution_days: float | None
    wards: list[WardStats]


def get_redis_client() -> redis.Redis:
    return redis.Redis.from_url(settings.REDIS_URL, decode_responses=True, socket_connect_timeout=1)


def _duration_days():
    return func.extract("epoch", Complaint.updated_at - Complaint.created_at) / 86400.0


def build_public_stats(db: Session) -> PublicStats:
    resolved = Complaint.status == "RESOLVED"
    totals = db.query(
        func.count(Complaint.id).label("total"),
        func.count(case((resolved, 1))).label("resolved"),
        func.avg(case((resolved, _duration_days()))).label("average_days"),
    ).one()
    total_count = int(totals.total or 0)
    resolved_count = int(totals.resolved or 0)
    ward_rows = (
        db.query(
            Complaint.ward_id.label("ward_id"),
            Complaint.department_name.label("department_name"),
            func.count(Complaint.id).label("total"),
            func.count(case((resolved, 1))).label("resolved"),
            func.avg(case((resolved, _duration_days()))).label("average_days"),
        )
        .filter(Complaint.ward_id.isnot(None))
        .group_by(Complaint.ward_id, Complaint.department_name)
        .order_by(Complaint.ward_id, Complaint.department_name)
        .all()
    )
    wards = []
    for row in ward_rows:
        ward_total = int(row.total or 0)
        ward_resolved = int(row.resolved or 0)
        wards.append(WardStats(
            ward_id=row.ward_id,
            department_name=row.department_name,
            total_complaints=ward_total,
            resolved_complaints=ward_resolved,
            resolution_rate=round(ward_resolved / ward_total * 100, 1) if ward_total else 0.0,
            average_resolution_days=round(float(row.average_days), 1) if row.average_days is not None else None,
        ))
    average = totals.average_days
    return PublicStats(
        generated_at=datetime.now().astimezone(),
        total_complaints=total_count,
        resolved_complaints=resolved_count,
        resolution_rate=round(resolved_count / total_count * 100, 1) if total_count else 0.0,
        average_resolution_days=round(float(average), 1) if average is not None else None,
        wards=wards,
    )


@router.get("/stats", response_model=PublicStats)
def get_public_stats(db: Session = Depends(get_db)) -> PublicStats:
    """Publish aggregate complaint statistics, cached for five minutes."""
    client: Any | None = None
    cache_read_failed = False
    try:
        client = get_redis_client()
        cached = client.get(CACHE_KEY)
        if cached:
            result = PublicStats.model_validate_json(cached)
            client.close()
            return result
    except (redis.RedisError, ValueError, TypeError):
        logger.warning("Public stats cache read failed; computing fresh data", exc_info=True)
        if client is not None:
            try:
                client.close()
            except redis.RedisError:
                logger.debug("Failed to close Redis client", exc_info=True)
        client = None
        cache_read_failed = True

    try:
        stats = build_public_stats(db)
    except Exception as exc:
        logger.exception("Failed to compute public complaint statistics")
        raise HTTPException(status_code=503, detail="Public statistics are temporarily unavailable") from exc

    if cache_read_failed:
        return stats
    if client is None:
        try:
            client = get_redis_client()
        except (redis.RedisError, ValueError):
            logger.warning("Public stats cache unavailable; returning database result", exc_info=True)
            return stats
    try:
        client.set(CACHE_KEY, json.dumps(stats.model_dump(mode="json")), ex=settings.PUBLIC_STATS_CACHE_TTL_SECONDS)
    except redis.RedisError:
        logger.warning("Public stats cache write failed; returning database result", exc_info=True)
    finally:
        try:
            client.close()
        except redis.RedisError:
            logger.debug("Failed to close Redis client", exc_info=True)
    return stats
