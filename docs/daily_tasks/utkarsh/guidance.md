# Detailed Daily Task Guidance — Utkarsh Mishra (Backend & Database)

**Developer:** Utkarsh Mishra  
**Domain:** Backend API / Neon PostgreSQL + PostGIS DB / Clerk Auth Verification / Routing & SLA Engine  
**Working Directory:** `backend/`

---

## Structure of Daily Guidance
Each day includes:
1. **Purpose:** Why this backend feature/schema is being built and how it serves the platform.
2. **What to Do:** Detailed architectural, database, and API implementation steps.
3. **What to Expect:** API endpoints, HTTP status codes, request/response models, database queries.
4. **What to Check / Valid Output:** Exact verification commands, SQL queries, and expected JSON outputs.

---

# Phase 1: Core API, Spatial DB & Auth Verification (Days 1–7)

## Day 1: FastAPI Scaffolding, Pydantic Config & DB Session
* **Purpose:** Set up a clean, scalable FastAPI application structure with environment variable management, database connection pooling, and health check endpoints.
* **What to Do:**
  1. Initialize directory structure inside `backend/`:
     - `app/main.py`, `app/core/config.py`, `app/db/session.py`, `app/api/v1/`, `app/models/`, `app/schemas/`.
  2. Install dependencies: `pip install fastapi uvicorn pydantic-settings sqlalchemy psycopg2-binary alembic`.
  3. Create `app/core/config.py` using Pydantic `BaseSettings` loading `NEON_DATABASE_URL`, `CLERK_SECRET_KEY`, `REDIS_URL`.
  4. Build `app/db/session.py` with SQLAlchemy `create_engine` (pool size 10, max overflow 20).
  5. Create health endpoint `GET /health` returning DB connection status.
* **What to Expect:** Fast, async API server serving Swagger docs at `http://localhost:8000/docs`.
* **What to Check / Valid Output:**
  ```bash
  cd backend
  pytest tests/test_health.py
  ```
  *Output:* `curl http://localhost:8000/health` returns HTTP 200 `{"status": "healthy", "database": "connected"}`.

---

## Day 2: Clerk JWT Authentication Middleware & Security Dependency
* **Purpose:** Protect backend API routes by verifying JWT tokens issued by Clerk, ensuring only authenticated citizens and authorized officers can perform mutations.
* **What to Do:**
  1. Install `python-jose[cryptography]` and `requests`.
  2. Create `app/core/auth.py`:
     - Fetch Clerk's public JSON Web Key Set (JWKS) from `https://api.clerk.dev/v1/jwks`.
     - Build `get_current_user` FastAPI `Depends` function that extracts `Authorization: Bearer <token>`, decodes JWT signature, and returns user payload (`user_id`, `email`, `role`).
  3. Create protected route `GET /api/v1/users/me`.
* **What to Expect:** Incoming HTTP requests without valid bearer tokens are rejected immediately with HTTP 401 Unauthorized.
* **What to Check / Valid Output:**
  - `curl -H "Authorization: Bearer invalid_token" http://localhost:8000/api/v1/users/me` returns HTTP 401 `{"detail": "Invalid or expired token"}`.

---

## Day 3: PostGIS Extension & Spatial Database Models
* **Purpose:** Store citizen report coordinates in a true geospatial database (PostGIS) to enable high-speed distance queries and spatial clustering.
* **What to Do:**
  1. Install `GeoAlchemy2` and `Shapely`.
  2. Enable PostGIS on Neon DB: `CREATE EXTENSION IF NOT EXISTS postgis;`.
  3. Create `app/models/complaint.py`:
     ```python
     class Complaint(Base):
         __tablename__ = "complaints"
         id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
         user_id = Column(String, nullable=False)
         category = Column(String, nullable=False)
         description = Column(Text)
         image_url = Column(String, nullable=False)
         severity_score = Column(Float, default=0.0)
         severity_level = Column(String, default="PENDING")
         status = Column(String, default="RECEIVED")
         upvote_count = Column(Integer, default=1)
         location = Column(Geometry("POINT", srid=4326), nullable=False)
         created_at = Column(DateTime(timezone=True), server_default=func.now())
     ```
  4. Generate and run Alembic migration: `alembic revision --autogenerate -m "Add PostGIS complaint table"` $\rightarrow$ `alembic upgrade head`.
* **What to Expect:** Spatial table `complaints` created in Neon PostgreSQL with geometry column `location`.
* **What to Check / Valid Output:**
  - Execute SQL query `SELECT ST_AsText(location) FROM complaints;` returning PostGIS `POINT(lng lat)`.

---

## Day 4: Complaint Creation Endpoint & Storage Integration
* **Purpose:** Accept citizen multipart report submissions (photo + spatial metadata), upload image to cloud storage, and write PostGIS spatial records.
* **What to Do:**
  1. Create `app/services/storage.py` integrating Supabase Storage or AWS S3 SDK (`boto3`).
  2. Build `POST /api/v1/complaints`:
     - Parameters: `file: UploadFile`, `latitude: float`, `longitude: float`, `category: str`, `description: Optional[str]`.
     - Upload file to storage and get public URL.
     - Convert lat/lng to WKT element: `from WKTElement import WKTElement; location = WKTElement(f'POINT({longitude} {latitude})', srid=4326)`.
     - Save to DB and return HTTP 201 Created.
* **What to Expect:** API ingests photo and lat/lng, stores image in cloud, and saves spatial point in PostGIS.
* **What to Check / Valid Output:**
  - Response JSON:
    ```json
    {
      "id": "c7a8f9e1-...",
      "status": "RECEIVED",
      "image_url": "https://storage.supabase.co/...",
      "location": {"lat": 19.218321, "lng": 72.873145}
    }
    ```

---

## Day 5: AI Engine Service Integration
* **Purpose:** Enrich complaint records with automated AI severity scores and damage classification outputs upon submission.
* **What to Do:**
  1. Import `ai_engine` severity scoring modules into `app/services/ai_service.py`.
  2. Modify `POST /api/v1/complaints` flow:
     - Read image bytes $\rightarrow$ pass to AI analysis function.
     - Extract `ai_category`, `severity_score`, `severity_level` (`CRITICAL`, `MODERATE`, `MINOR`).
     - Save enrichment metadata to complaint DB row.
* **What to Expect:** Complaints are automatically categorized and severity-graded upon creation.
* **What to Check / Valid Output:**
  - Query DB row for uploaded pothole: `severity_level` is automatically populated as `'CRITICAL'`.

---

## Day 6: Celery + Redis Asynchronous Worker Queue
* **Purpose:** Offload heavy ML inference from the HTTP request loop so API response times remain under 300ms.
* **What to Do:**
  1. Install `celery` and `redis`.
  2. Create `app/core/celery_app.py` configured with Redis broker URL.
  3. Create task `app/tasks/ai_tasks.py`: `@celery_app.task def process_complaint_ai_task(complaint_id: str): ...`.
  4. Update `POST /api/v1/complaints` to save raw complaint with status `'PROCESSING'` and dispatch Celery task asynchronously, returning HTTP 202 Accepted.
* **What to Expect:** HTTP API responds instantly (<250ms); Celery worker executes inference in background thread and updates DB when finished.
* **What to Check / Valid Output:**
  ```bash
  celery -A app.core.celery_app worker --loglevel=info
  ```
  *Output:* Celery log shows `Task process_complaint_ai_task[...] succeeded in 1.2s`.

---

## Day 7: Phase 1 Integration Test Pass
* **Purpose:** Ensure all core API endpoints, auth verification, PostGIS storage, and Celery workers operate seamlessly.
* **What to Do:**
  1. Run integration test suite `pytest tests/integration/test_phase1.py`.
* **What to Check / Valid Output:**
  - All test assertions pass 100%.

---

# Phase 2: Spatial Queries, Deduplication & Queue APIs (Days 8–14)

## Day 8: PostGIS Spatial Proximity Search Endpoint
* **Purpose:** Find open complaints within a given geographic radius to detect duplicate reports.
* **What to Do:**
  1. Build `GET /api/v1/complaints/nearby`:
     - Parameters: `latitude: float`, `longitude: float`, `radius_meters: float = 15.0`.
     - Execute PostGIS query using `ST_DWithin`:
       ```python
       query = session.query(Complaint).filter(
           func.ST_DWithin(
               Complaint.location,
               func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326),
               radius_meters / 111320.0  # Approx degree conversion
           ),
           Complaint.status != 'RESOLVED'
       )
       ```
* **What to Expect:** Returns JSON array of open complaints within exact physical radius.
* **What to Check / Valid Output:**
  - Test request with coordinates 10m away from existing ticket returns matching ticket; coordinates 500m away return empty list `[]`.

---

## Day 9: Complaint Upvoting & Automated Merging API
* **Purpose:** Allow citizens to upvote existing issues instead of creating redundant database rows.
* **What to Do:**
  1. Build `POST /api/v1/complaints/{id}/upvote`:
     - Check if ticket exists and is open.
     - Increment `upvote_count` by 1.
     - Create entry in `complaint_upvotes` join table (`complaint_id`, `user_id`, `created_at`).
* **What to Expect:** Ticket upvote counter increases; user relation recorded to prevent duplicate upvotes from same account.
* **What to Check / Valid Output:**
  - Response JSON: `{"complaint_id": "...", "upvote_count": 2, "message": "Upvote recorded successfully"}`.

---

## Day 10: Authority Complaint Queue API
* **Purpose:** Serve Ward Officers and PWD admins a high-density, paginated queue of complaints sorted by severity score.
* **What to Do:**
  1. Build `GET /api/v1/authority/complaints`:
     - Parameters: `page: int = 1`, `limit: int = 20`, `status: Optional[str]`, `severity: Optional[str]`, `ward_id: Optional[str]`.
     - RBAC check: Require `role` in `['WARD_OFFICER', 'ADMIN']`.
     - Query complaints ordered by `severity_score.desc()`, `created_at.desc()`.
* **What to Expect:** Secured queue API returning paginated JSON result set with total count.
* **What to Check / Valid Output:**
  - Request without officer role returns HTTP 403 Forbidden. Request with officer token returns paginated queue.

---

## Day 11: Geospatial Hotspot GeoJSON API
* **Purpose:** Supply spatial cluster data to the frontend heatmap layer.
* **What to Do:**
  1. Build `GET /api/v1/analytics/hotspots`:
     - Fetch spatial cluster results from `ai_engine` DBSCAN algorithm.
     - Format into GeoJSON `FeatureCollection`:
       ```json
       {
         "type": "FeatureCollection",
         "features": [
           {
             "type": "Feature",
             "geometry": { "type": "Point", "coordinates": [72.8731, 19.2183] },
             "properties": { "cluster_id": 1, "complaint_count": 8, "avg_severity": 84.5 }
           }
         ]
       }
       ```
* **What to Expect:** Perfectly formatted GeoJSON output ready for map rendering.
* **What to Check / Valid Output:**
  - Output passes GeoJSON specification validator with zero schema errors.

---

## Day 12: Status Machine & Action Update API
* **Purpose:** Enforce valid state transitions when officers change complaint statuses.
* **What to Do:**
  1. Build `PATCH /api/v1/authority/complaints/{id}/status`:
     - Schema: `status: str`, `contractor_name: Optional[str]`, `notes: Optional[str]`, `resolution_image_url: Optional[str]`.
     - State machine validation:
       - `RECEIVED` $\rightarrow$ `ASSIGNED`
       - `ASSIGNED` $\rightarrow$ `IN_REPAIR`
       - `IN_REPAIR` $\rightarrow$ `RESOLVED` (requires `resolution_image_url`).
* **What to Expect:** Invalid state jumps (e.g. `RECEIVED` directly to `RESOLVED`) are rejected with HTTP 400.
* **What to Check / Valid Output:**
  - Attempting invalid state transition returns HTTP 400 `{"detail": "Invalid status transition"}`.

---

## Day 13: Dynamic Query Builder & Filter Optimization
* **Purpose:** Maintain sub-50ms database response times under complex search filter combinations.
* **What to Do:**
  1. Build dynamic filter query builder using SQLAlchemy `and_()` expressions.
  2. Create database indexes:
     - `CREATE INDEX idx_complaints_status_severity ON complaints(status, severity_level);`
     - `CREATE INDEX idx_complaints_location ON complaints USING GIST(location);`
* **What to Expect:** Fast execution of complex queries even on large datasets.
* **What to Check / Valid Output:**
  - Run SQL `EXPLAIN ANALYZE` on filter query; verify index scan is utilized instead of sequential scan.

---

## Day 14: Phase 2 Integration Test Pass
* **Purpose:** Validate spatial queries, deduplication APIs, authority queues, and state transitions.
* **What to Do:** Run `pytest tests/integration/test_phase2.py`.
* **What to Check / Valid Output:** 100% test pass.

---

# Phase 3: Auto-Routing, SLA Escalation & Audit Trail (Days 15–21)

## Day 15: Municipal Polygon Jurisdiction Auto-Routing
* **Purpose:** Automatically determine which ward or agency (PWD vs Local Ward) owns a reported complaint based on GPS location.
* **What to Do:**
  1. Create PostGIS table `ward_boundaries` (`id`, `name`, `geom Geometry(POLYGON, 4326)`).
  2. Build Auto-Routing engine:
     ```python
     ward = session.query(WardBoundary).filter(
         func.ST_Intersects(WardBoundary.geom, complaint.location)
     ).first()
     complaint.assigned_ward_id = ward.id if ward else "CENTRAL_PWD"
     ```
* **What to Expect:** Every submitted complaint is instantly tagged with its governing ward ID.
* **What to Check / Valid Output:**
  - Submitting coordinates inside Ward 3 polygon sets `assigned_ward_id = "WARD_3"`.

---

## Day 16: Celery Beat SLA Periodic Escalation Worker
* **Purpose:** Monitor unresolved tickets and automatically escalate those exceeding their SLA deadlines.
* **What to Do:**
  1. Configure Celery Beat schedule in `app/core/celery_app.py` running every 30 minutes.
  2. Create task `check_sla_deadlines`:
     - Find tickets where `status != 'RESOLVED'` and `now() - created_at > SLA_LIMIT`.
     - SLA limits: `CRITICAL` = 48 hours, `MODERATE` = 7 days, `MINOR` = 30 days.
     - Action: Increment `escalation_level`, update status to `'ESCALATED'`, insert notification log.
* **What to Expect:** Overdue tickets automatically transition to escalated status without human intervention.
* **What to Check / Valid Output:**
  - Manually backdated ticket is picked up by Celery Beat worker and marked `ESCALATED`.

---

## Day 17: Public Analytics API & Redis Caching
* **Purpose:** Serve high-traffic public transparency stats without stressing the PostgreSQL database.
* **What to Do:**
  1. Build `GET /api/v1/public/stats`.
  2. Integrate Redis caching (`redis-py`):
     - Check Redis key `public_stats_cache`. If present, return cached JSON immediately.
     - If cache miss, compute metrics from DB, store in Redis with TTL = 300 seconds (5 mins), and return.
* **What to Expect:** Response time drops from ~200ms to <5ms on cached hits.
* **What to Check / Valid Output:**
  - Response headers show `X-Cache: HIT` on second request; response time $<5\text{ms}$.

---

## Day 18: Notification Engine & Trigger Service
* **Purpose:** Dispatch in-app alerts and email updates to citizens when ticket statuses change.
* **What to Do:**
  1. Create `notifications` table (`id`, `user_id`, `complaint_id`, `message`, `is_read`, `created_at`).
  2. Build `app/services/notification_service.py` to create notification rows and send emails via SendGrid / Nodemailer API.
  3. Wire triggers on status edits and SLA escalations.
* **What to Expect:** Status changes generate DB notification rows and trigger outgoing emails.
* **What to Check / Valid Output:**
  - Editing complaint status inserts row into `notifications` table for reporting citizen.

---

## Day 19: Role-Based Access Control (RBAC) Hardening
* **Purpose:** Lock down all administrative endpoints against unauthorized access attempts.
* **What to Do:**
  1. Create reusable FastAPI dependency `require_roles(allowed_roles: List[str])`:
     ```python
     def require_roles(allowed_roles: List[str]):
         def dependency(user = Depends(get_current_user)):
             if user.role not in allowed_roles:
                 raise HTTPException(status_code=403, detail="Permission denied")
             return user
         return dependency
     ```
  2. Apply to all authority endpoints (`/api/v1/authority/*`).
* **What to Expect:** Unauthorized access attempts return HTTP 403 Forbidden.
* **What to Check / Valid Output:**
  - `pytest tests/test_rbac.py` confirms citizen tokens are denied access to admin routes.

---

## Day 20: Governance Audit Logging Infrastructure
* **Purpose:** Maintain an unalterable, chronological log of every change made to every complaint for legal accountability.
* **What to Do:**
  1. Create `audit_logs` table (`id`, `complaint_id`, `actor_id`, `actor_role`, `previous_state`, `new_state`, `ip_address`, `timestamp`).
  2. Create backend listener writing an audit row on every `Complaint` table update.
  3. Build `GET /api/v1/authority/complaints/{id}/audit`.
* **What to Expect:** Immutable audit log tracking every system and officer action.
* **What to Check / Valid Output:**
  - Updating a complaint creates a new immutable row in `audit_logs`.

---

## Day 21: Phase 3 Integration Test Pass
* **Purpose:** Verify routing, SLA escalation, caching, notifications, RBAC, and audit logs.
* **What to Do:** Run `pytest tests/integration/test_phase3.py`.
* **What to Check / Valid Output:** 100% test pass.

---

# Phase 4: Production Tuning & Staging Deployment (Days 22–30)

## Days 22–24: PostGIS Query Optimization & Indexing
* **Purpose:** Ensure database handles thousands of concurrent spatial requests efficiently.
* **What to Do:** Audit PostGIS queries, add spatial GIST indexes, optimize connection pooling.

## Days 25–27: Production Dockerization & Docker Compose
* **Purpose:** Package FastAPI backend, Celery worker, and Redis into reproducible containers.
* **What to Do:** Create `backend/Dockerfile` and root `docker-compose.yml`. Ensure clean startup.

## Days 28–30: Cloud Deployment & Render Live Staging
* **Purpose:** Deploy live staging environment for public demo.
* **What to Do:** Deploy FastAPI backend to Render, connect Neon PostgreSQL, verify HTTPS APIs, and perform final smoke test.
