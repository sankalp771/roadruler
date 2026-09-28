"""Generate a deterministic, explicitly opt-in synthetic Mumbai complaint set.

Default invocation is a dry run. Database writes require both ``--apply`` and
an explicitly supplied ``--database-url``. Supply a real image URL template
whose path includes ``{index}`` only when those image objects already exist.
"""

import argparse
import json
import random
import sys
import uuid
from pathlib import Path
from urllib.parse import urlparse

from geoalchemy2.elements import WKTElement

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

AREAS = (
    ("KANDIVALI", 19.2108, 72.8726, 38),
    ("MALAD", 19.1860, 72.8480, 37),
    ("ANDHERI", 19.1197, 72.8464, 38),
    ("BORIVALI", 19.2307, 72.8567, 37),
)
CATEGORIES = (
    ("POTHOLE", "Pothole"),
    ("WATERLOGGING", "Waterlogging"),
    ("CRACK", "Road crack"),
)
SEVERITIES = (("CRITICAL", 70.0, 100.0), ("MODERATE", 35.0, 69.9), ("MINOR", 1.0, 34.9))
STATUSES = ("RECEIVED", "ASSIGNED", "IN_REPAIR")
SEED_NAMESPACE = uuid.UUID("e3ff46ed-e923-4b66-92a0-64972fd98a8b")


def generate_records(seed: int = 20260923, image_url_template: str | None = None) -> list[dict]:
    """Create reproducible synthetic complaints centered on four Mumbai areas."""
    rng = random.Random(seed)
    records: list[dict] = []
    index = 0
    for area, center_lat, center_lng, count in AREAS:
        for _ in range(count):
            index += 1
            category, ai_category = CATEGORIES[(index - 1) % len(CATEGORIES)]
            severity_level, minimum, maximum = SEVERITIES[(index - 1) % len(SEVERITIES)]
            records.append(
                {
                    "id": str(uuid.uuid5(SEED_NAMESPACE, f"{seed}:{index}")),
                    "user_id": "synthetic-seed-generator",
                    "category": category,
                    "ai_category": ai_category,
                    "description": f"Synthetic {ai_category.lower()} report near {area.title()}.",
                    "image_url": image_url_template.format(index=index) if image_url_template else None,
                    "severity_score": round(rng.uniform(minimum, maximum), 2),
                    "severity_level": severity_level,
                    "detections_count": 1,
                    "status": STATUSES[(index - 1) % len(STATUSES)],
                    "upvote_count": rng.randint(1, 18),
                    "ward_id": f"SYNTHETIC_{area}",
                    "latitude": round(max(-90, min(90, rng.gauss(center_lat, 0.0012))), 6),
                    "longitude": round(max(-180, min(180, rng.gauss(center_lng, 0.0012))), 6),
                }
            )
    return records


def _validate_image_template(template: str) -> None:
    try:
        sample_url = template.format(index=1)
    except (KeyError, ValueError) as exc:
        raise ValueError("image URL template must format with {index}") from exc
    parsed = urlparse(sample_url)
    if parsed.scheme != "https" or not parsed.netloc or parsed.hostname in {"example.invalid", "example.test"}:
        raise ValueError("image URL template must use HTTPS and point to existing image objects")


def _seed_database(database_url: str, records: list[dict]) -> int:
    from sqlalchemy import create_engine
    from sqlalchemy.dialects.postgresql import insert

    from app.models.complaint import Complaint

    values = [
        {
            **{key: value for key, value in record.items() if key not in {"latitude", "longitude"}},
            "location": WKTElement(f"POINT({record['longitude']} {record['latitude']})", srid=4326),
        }
        for record in records
    ]
    engine = create_engine(database_url, pool_pre_ping=True)
    try:
        with engine.begin() as connection:
            result = connection.execute(
                insert(Complaint).values(values).on_conflict_do_nothing(index_elements=["id"])
            )
            return result.rowcount or 0
    finally:
        engine.dispose()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    run_mode = parser.add_mutually_exclusive_group()
    run_mode.add_argument("--apply", action="store_true", help="Insert synthetic records into the explicitly named database")
    run_mode.add_argument("--dry-run", action="store_true", help="Generate and summarize records without database writes (default)")
    parser.add_argument("--database-url", help="Database URL; required with --apply and never read implicitly from env")
    parser.add_argument("--image-url-template", help="HTTPS template for existing photos, containing {index}")
    parser.add_argument("--seed", type=int, default=20260923)
    args = parser.parse_args()
    if args.apply and (not args.database_url or not args.image_url_template):
        parser.error("--apply requires both --database-url and --image-url-template")
    if args.image_url_template:
        try:
            _validate_image_template(args.image_url_template)
        except ValueError as exc:
            parser.error(str(exc))

    records = generate_records(args.seed, args.image_url_template)
    area_counts = {area: count for area, _lat, _lng, count in AREAS}
    if not args.apply:
        print(json.dumps({"generated": len(records), "areas": area_counts, "database_writes": False}, indent=2))
        return 0

    inserted = _seed_database(args.database_url, records)
    print(json.dumps({"generated": len(records), "inserted": inserted, "already_present": len(records) - inserted}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
