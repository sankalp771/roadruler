# Weekly Integration Testing Protocol

This document outlines the mandatory end-of-week integration tests that must be executed across the complete stack (**Frontend**, **Backend**, **AI Engine**).

---

## Integration Test Suite Architecture

```
tests/integration/
├── test_phase1.py  # Auth, Geo-tag upload, YOLO severity, PostGIS save
├── test_phase2.py  # Spatial deduplication, Upvoting, DBSCAN clustering, Authority queue
├── test_phase3.py  # Auto-routing, SLA escalation, Notifications, Audit trail
└── test_phase4.py  # End-to-End stress & load testing
```

---

## Phase 1 Integration Test (Day 7)
**Goal:** Validate core ingestion flow from citizen auth to AI severity tagging and PostGIS storage.

### Test Steps:
1. Obtain test Clerk JWT for citizen user.
2. Send `POST /api/v1/complaints` with:
   - Latitude: `19.2183`, Longitude: `72.8731` (Thakur College area)
   - Sample Pothole photo (`test_pothole.jpg`)
   - Category: `POTHOLE`
3. Assert API response status `202 Accepted` or `201 Created`.
4. Wait for Celery worker processing.
5. Query `GET /api/v1/complaints/{id}`:
   - Assert `severity_level` is `CRITICAL`.
   - Assert `location` geometry is correctly indexed in PostGIS.
   - Assert image stored in object storage with valid URL.

---

## Phase 2 Integration Test (Day 14)
**Goal:** Validate deduplication, upvoting, spatial clustering, and authority dashboard management.

### Test Steps:
1. Submit Complaint A at `(19.2183, 72.8731)` with photo X.
2. Submit Complaint B at `(19.2184, 72.8732)` (11 meters away) with visually identical photo X.
3. Assert system detects duplicate, increments `upvote_count`, and merges under Complaint A ID.
4. Submit 5 additional complaints in a 40-meter cluster around Thakur College.
5. Trigger DBSCAN clustering endpoint `GET /api/v1/analytics/hotspots`.
6. Assert output GeoJSON contains a cluster feature grouping the 5 complaints.
7. Log in as Ward Officer (`WARD_OFFICER` role) and fetch queue `GET /api/v1/authority/complaints`.
8. Update status of Complaint A to `IN_REPAIR`.
9. Assert status update succeeds and is reflected in citizen tracker UI.

---

## Phase 3 Integration Test (Day 21)
**Goal:** Validate municipal routing, SLA escalation, notification dispatch, and audit logging.

### Test Steps:
1. Submit complaint inside Ward 3 polygon boundaries.
2. Assert ticket is automatically assigned to `assigned_ward_id = 3`.
3. Manually update creation timestamp of ticket to 50 hours ago.
4. Trigger Celery Beat SLA worker cycle.
5. Assert ticket status changes to `ESCALATED` and `escalation_level = 1`.
6. Query `GET /api/v1/notifications` for reporting citizen.
7. Assert escalation notification is present in citizen notification array.
8. Query `GET /api/v1/authority/complaints/{id}/audit`.
9. Assert audit trail contains timestamped history of creation, status change, and escalation.

---

## Phase 4 Integration Test (Day 28)
**Goal:** Validate containerized Docker environment and load capabilities.

### Test Steps:
1. Execute `docker-compose up --build -d`.
2. Run concurrent load test with 50 simultaneous submissions.
3. Assert zero failed requests ($100\%$ success rate).
4. Assert maximum API response time $<500\text{ms}$.
