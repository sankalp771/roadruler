# Utkarsh Mishra - Deliverables & Verification Checklist
**Domain:** Backend API / Neon PostgreSQL + PostGIS DB / Clerk Auth / Routing & SLA Engine  
**Working Directory:** `backend/`

---

## Deliverables Checklist

### Phase 1: Core API & PostGIS Setup (Days 1–7)
- [x] **Day 1:** FastAPI application directory scaffolding, Pydantic settings config, Neon Postgres DB session, `/health` endpoint.
- [x] **Day 2:** Clerk JWT verification middleware, `get_current_user` dependency, `/api/v1/users/me` route.
- [ ] **Day 3:** PostGIS extension setup, `Complaint` spatial model with `GEOMETRY(Point, 4326)`, Alembic migrations.
- [ ] **Day 4:** `POST /api/v1/complaints` with Supabase/S3 storage upload and PostGIS point insertion.
- [ ] **Day 5:** Connect `ai_engine` severity module to complaint creation pipeline.
- [ ] **Day 6:** Celery task queue setup with Redis broker; async task `process_complaint_ai_task`.
- [ ] **Day 7:** Phase 1 End-to-End integration test pass with frontend.

### Phase 2: Proximity Querying, Deduplication & Queue Management (Days 8–14)
- [ ] **Day 8:** PostGIS spatial proximity query API `GET /api/v1/complaints/nearby`.
- [ ] **Day 9:** Upvoting & ticket merging endpoint `POST /api/v1/complaints/{id}/upvote`.
- [ ] **Day 10:** Authority Queue API `GET /api/v1/authority/complaints` with RBAC role validation.
- [ ] **Day 11:** Hotspot GeoJSON API `GET /api/v1/analytics/hotspots`.
- [ ] **Day 12:** Status Transition API `PATCH /api/v1/authority/complaints/{id}/status` with state machine checks.
- [ ] **Day 13:** Dynamic SQLAlchemy filter query builder supporting multi-parameter search.
- [ ] **Day 14:** Phase 2 End-to-End integration test pass.

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
