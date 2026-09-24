# Utkarsh Mishra - Deliverables & Verification Checklist
**Domain:** Backend API / Neon PostgreSQL + PostGIS DB / Clerk Auth / Routing & SLA Engine  
**Working Directory:** `backend/`

---

## Deliverables Checklist

### Phase 1: Core API & PostGIS Setup (Days 1–7)
- [x] **Day 1:** FastAPI application directory scaffolding, Pydantic settings config, Neon Postgres DB session, `/health` endpoint.
- [x] **Day 2:** Clerk JWT verification middleware, `get_current_user` dependency, `/api/v1/users/me` route.
- [x] **Day 3:** PostGIS extension setup, `Complaint` spatial model with `GEOMETRY(Point, 4326)`, Alembic migrations.
- [x] **Day 4:** `POST /api/v1/complaints` with Supabase/S3 storage upload and PostGIS point insertion.
- [x] **Day 5:** Connect `ai_engine` severity module to complaint creation pipeline and persist AI category, severity, and detection count.
- [x] **Day 6:** Celery task queue setup with Redis broker; async task `process_complaint_ai_task`.
- **Day 7: Phase 1 Integration**
  - [x] Owner-scoped complaint detail endpoint returns AI detection count and per-region class/confidence/box details; API response covered by tests.
  - [x] Backend lifecycle verified end to end: authenticated submission, Supabase image upload, Neon/PostGIS persistence, Redis/Celery dispatch, and AI enrichment.
  - [ ] Interactive Clerk browser submission and tracking flow remains unverified.

### Phase 2: Proximity Querying, Deduplication & Queue Management (Days 8–14)
- [x] **Day 8:** PostGIS spatial proximity query API `GET /api/v1/complaints/nearby` — migration applied; live PostGIS radius and validation checks pass.
- [x] **Day 9:** Upvoting & ticket merging endpoint `POST /api/v1/complaints/{id}/upvote` with one vote per citizen and supporter ticket access.
- [x] **Day 10:** Authority Queue API `GET /api/v1/authority/complaints` with pagination, status/severity/ward filters, severity ordering, and Ward Officer/Admin RBAC.
- [x] **Day 11:** Protected Hotspot GeoJSON API `GET /api/v1/analytics/hotspots`, backed by DBSCAN cluster summaries.
- [x] **Day 12:** Status Transition API `PATCH /api/v1/authority/complaints/{id}/status` with sequential state machine, required resolution evidence, contractor/notes fields, and append-only action history.
- [x] **Day 13:** Parameterized multi-filter authority query builder and status/severity composite index; verified index eligibility with `EXPLAIN ANALYZE`. Existing PostGIS location GIST index confirmed.
- [x] **Day 14:** Phase 2 end-to-end test covers PostGIS nearby lookup, upvote idempotency, queue filters, hotspots, evidence upload path, and status transitions.

### Phase 3: Auto-Routing, SLA Escalation & Security (Days 15–21)
- [ ] **Day 15:** PostGIS ward boundary spatial auto-routing engine using `ST_Intersects`.
- [ ] **Day 16:** Celery Beat periodic task checking SLA deadlines and escalating overdue tickets.
- [ ] **Day 17:** Public Analytics API `GET /api/v1/public/stats` with Redis caching.
- [ ] **Day 18:** Notification Service creating in-app alerts and sending emails on status change.
- [ ] **Day 19:** FastAPI RBAC dependencies `require_roles(["WARD_OFFICER", "ADMIN"])`.
- [ ] **Day 20:** Immutable Audit Logger writing state changes to `audit_logs` table.
- [ ] **Day 21:** Phase 3 End-to-End integration test pass.

### Phase 4: Performance Tuning & Staging (Days 22–30)
- [ ] **Days 22–24:** PostGIS spatial GIST index creation and query optimization.
- [ ] **Days 25–27:** Production Dockerfile and docker-compose orchestration.
- [ ] **Days 28–30:** Render backend deployment & live API verification.
