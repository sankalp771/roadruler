# Master Development Schedule & Production Blueprint (30 Days)

## Project Overview
**Crowdsourced Road Issue Reporter (`RoadRuler`)**  
A production-grade, AI-powered civic-tech platform designed for urban road infrastructure management.

---

## Team Ownership & Architecture Boundaries

```
d:\roadruler\
├── frontend/             <-- Milin Kanu (Vite + React, Leaflet.js, Clerk Auth, UI/UX)
├── backend/              <-- Utkarsh Mishra (FastAPI, Neon PostGIS, Clerk JWT, Routing, SLA)
├── ai_engine/            <-- Sankalp Pandey (PyTorch, YOLOv8, OpenCV, ResNet50, DBSCAN)
└── docs/                 <-- Shared Documentation, Logs, & Deliverables
```

---

## Detailed Daywise Production Roadmap

### Phase 1: Foundation, Auth & Core AI Ingestion (Days 1–7)

#### Day 1: System Scaffolding & Health Interfaces
- **Milin (`frontend/`):** Scaffolding Vite React app with TailwindCSS design system (`Inter` font, HSL color tokens, dark mode support), React Router v6.
  - *Verification:* `npm run build` succeeds with zero errors.
- **Utkarsh (`backend/`):** FastAPI directory structure, Pydantic settings config, Neon Postgres DB session, `/health` endpoint.
  - *Verification:* `curl http://localhost:8000/health` returns `{"status":"healthy","db":"connected"}`.
- **Sankalp (`ai_engine/`):** Python ML environment, YOLOv8 inference wrapper class `RoadDamageDetector`.
  - *Verification:* Running inference on test image returns bounding box JSON.

#### Day 2: Authentication & Security Middleware
- **Milin (`frontend/`):** Clerk React SDK integration, `<ClerkProvider>`, login/signup modals, protected route guards.
  - *Verification:* Accessing protected route redirects to Clerk Auth.
- **Utkarsh (`backend/`):** Clerk JWT verification middleware, `get_current_user` dependency, `/api/v1/users/me`.
  - *Verification:* Request with valid Bearer token returns 200; invalid token returns 401.
- **Sankalp (`ai_engine/`):** RDD2022 dataset formatting script converting annotations to YOLO format.
  - *Verification:* Dataset validation script prints valid label counts for Pothole, Crack, Waterlogging.

#### Day 3: Map Picker & PostGIS Spatial DB
- **Milin (`frontend/`):** Leaflet.js + OpenStreetMap `<LocationPickerMap />` with draggable marker & user geolocation.
  - *Verification:* Dragging marker updates coordinate state in real time.
- **Utkarsh (`backend/`):** PostGIS extension setup, `Complaint` spatial model with `GEOMETRY(Point, 4326)` column, Alembic migration.
  - *Verification:* `SELECT PostGIS_Full_Version();` returns active PostGIS extension.
- **Sankalp (`ai_engine/`):** YOLOv8 model training on road damage classes; export `best.pt`.
  - *Verification:* Training validation mAP@0.5 score $>0.80$.

#### Day 4: Report Submission & Storage Integration
- **Milin (`frontend/`):** `<ReportIssueForm />` with photo upload preview, category dropdown, description, map location.
  - *Verification:* Submitting form passes multipart data payload.
- **Utkarsh (`backend/`):** `POST /api/v1/complaints` with Supabase/S3 storage upload and PostGIS point insertion.
  - *Verification:* Returns HTTP 201 Created with complaint ID and image URL.
- **Sankalp (`ai_engine/`):** Damage Severity Score calculator combining bounding box area ratio and class weights.
  - *Verification:* Pothole bounding box $>10\%$ image area tags severity as `CRITICAL`.

#### Day 5: AI Engine Auto-Enrichment
- **Milin (`frontend/`):** `<ComplaintTracker />` view displaying ticket status timeline and metadata.
  - *Verification:* Viewing complaint renders details and location map correctly.
- **Utkarsh (`backend/`):** Connect `ai_engine` severity function to complaint creation pipeline.
  - *Verification:* `POST /api/v1/complaints` automatically populates DB severity columns.
- **Sankalp (`ai_engine/`):** ResNet50 2048-dim feature vector generator for visual duplicate matching.
  - *Verification:* Cosine similarity between 2 photos of same pothole is $>0.85$.

#### Day 6: Celery + Redis Asynchronous Task Processing
- **Milin (`frontend/`):** Toast notifications (`react-hot-toast`) and optimistic loading feedback.
  - *Verification:* Submitting shows toast *"Report queued for AI analysis"*.
- **Utkarsh (`backend/`):** Celery task queue setup with Redis broker; `process_complaint_ai_task`.
  - *Verification:* API returns HTTP 202 instantly; Celery worker runs inference in background.
- **Sankalp (`ai_engine/`):** Single entrypoint function `analyze_road_issue(image_bytes)` for worker context.
  - *Verification:* Celery worker processes 20 sequential images without memory leaks.

#### Day 7: Phase 1 Weekly Integration Test
- **Team Integration:** Execute end-to-end integration test suite `tests/integration/test_phase1.py`.

---

### Phase 2: Deduplication, Hotspots & Authority Portal (Days 8–14)

#### Day 8: Spatial Proximity & Visual Deduplication
- **Milin (`frontend/`):** Render nearby open complaints (yellow pins) on map during selection.
  - *Verification:* Map displays nearby report pins within 50m radius.
- **Utkarsh (`backend/`):** PostGIS proximity query API `GET /api/v1/complaints/nearby`.
  - *Verification:* Query returns list of complaints within 15m PostGIS radius.
- **Sankalp (`ai_engine/`):** Spatial + visual deduplication pipeline (`check_duplicate`).
  - *Verification:* Submitting duplicate photo within 15m radius returns duplicate match ID.

#### Day 9: Upvoting & Automated Ticket Merging
- **Milin (`frontend/`):** `<DuplicateWarningModal />` asking user to upvote existing ticket.
  - *Verification:* Tapping upvote calls API and redirects to existing ticket tracker.
- **Utkarsh (`backend/`):** `POST /api/v1/complaints/{id}/upvote` endpoint incrementing `upvote_count`.
  - *Verification:* Upvoting increases ticket `upvote_count` by 1.
- **Sankalp (`ai_engine/`):** Deduplication benchmark suite on test dataset.
  - *Verification:* Benchmark report confirms $>90\%$ deduplication precision.

#### Day 10: Authority Dashboard Core Layout
- **Milin (`frontend/`):** Authority Dashboard layout `/authority` with metrics cards, sidebar, table.
  - *Verification:* Responsive admin layout renders ticket table correctly.
- **Utkarsh (`backend/`):** Authority Queue API `GET /api/v1/authority/complaints` with RBAC checks.
  - *Verification:* Request from Citizen returns HTTP 403; Ward Officer receives paginated queue.
- **Sankalp (`ai_engine/`):** DBSCAN Geo-Spatial Clustering engine (`clustering.py`).
  - *Verification:* Dense coordinate points are assigned matching cluster IDs.

#### Day 11: Geospatial Hotspot Mapping & GeoJSON API
- **Milin (`frontend/`):** Heatmap Layer on Leaflet map using `leaflet.heat`.
  - *Verification:* Red intensity heatmaps align with high-density complaint clusters.
- **Utkarsh (`backend/`):** Hotspot GeoJSON API `GET /api/v1/analytics/hotspots`.
  - *Verification:* Output conforms to GeoJSON `FeatureCollection` standard.
- **Sankalp (`ai_engine/`):** Cluster Severity Summarizer ranking spatial zones by priority.
  - *Verification:* High-density cluster tagged as `HIGH_RISK_ZONE`.

#### Day 12: Work Order Assignment Workflows
- **Milin (`frontend/`):** `<ComplaintActionModal />` for status updates, contractor assignment, and notes.
  - *Verification:* Submitting action updates status badge to `ASSIGNED`.
- **Utkarsh (`backend/`):** Status Transition API `PATCH /api/v1/authority/complaints/{id}/status`.
  - *Verification:* Invalid state transition attempt returns HTTP 400 Bad Request.
- **Sankalp (`ai_engine/`):** Image Evidence Bounding Box Annotator saving annotated evidence JPEG.
  - *Verification:* Saved image includes bounding box rects and confidence score labels.

#### Day 13: Search, Filter & Synthetic Data Seeding
- **Milin (`frontend/`):** Multi-parameter Search & Filter toolbar.
  - *Verification:* Filtering by "CRITICAL" updates table rows instantly.
- **Utkarsh (`backend/`):** Dynamic SQLAlchemy filter query builder.
  - *Verification:* Filter query executes in $<50\text{ms}$ on PostGIS DB.
- **Sankalp (`ai_engine/`):** Synthetic Data Generator `seed_data.py` seeding 150 test complaints.
  - *Verification:* DB contains test complaints across Mumbai wards.

#### Day 14: Phase 2 Weekly Integration Test
- **Team Integration:** Execute `tests/integration/test_phase2.py`.

---

### Phase 3: Auto-Routing, SLA Escalation & Security (Days 15–21)

#### Day 15: Municipal Jurisdiction Routing
- **Milin (`frontend/`):** Department Ownership Badge on complaint cards.
  - *Verification:* Card renders assigned department name correctly.
- **Utkarsh (`backend/`):** PostGIS ward boundary spatial routing using `ST_Intersects`.
  - *Verification:* Coordinates inside Ward 3 polygon automatically assign `ward_id = 3`.
- **Sankalp (`ai_engine/`):** Image Quality Filter detecting blurriness (Laplacian variance) and corruption.
  - *Verification:* Extremely blurry photo rejected with `LOW_QUALITY_IMAGE`.

#### Day 16: SLA Monitoring & Escalation Worker
- **Milin (`frontend/`):** SLA Countdown Timer on task cards.
  - *Verification:* Ticket near SLA breach displays red alert timer.
- **Utkarsh (`backend/`):** Celery Beat periodic task checking SLA deadlines and escalating overdue tickets.
  - *Verification:* Backdated ticket status automatically updates to `ESCALATED`.
- **Sankalp (`ai_engine/`):** "Before & After" Repair Verification module comparing pre/post repair photos.
  - *Verification:* Clean repaired road photo vs pothole photo returns `REPAIR_CONFIRMED`.

#### Day 17: Public Transparency Portal
- **Milin (`frontend/`):** Public Transparency Portal homepage `/public`.
  - *Verification:* Renders resolution metrics and live statistics without auth.
- **Utkarsh (`backend/`):** Public Analytics API `GET /api/v1/public/stats` with Redis caching.
  - *Verification:* API response served in $<5\text{ms}$ from Redis cache.
- **Sankalp (`ai_engine/`):** ML evaluation charts (PR curves, Confusion Matrix) exported to deliverables.
  - *Verification:* Evaluation script generates clean PNG metric plots.

#### Day 18: Notification Center & Model Optimization
- **Milin (`frontend/`):** Notification Bell dropdown in header.
  - *Verification:* Unread notification badge updates dynamically.
- **Utkarsh (`backend/`):** Notification Service creating in-app alerts and sending emails.
  - *Verification:* Status edit creates notification row in DB and sends email log.
- **Sankalp (`ai_engine/`):** YOLO model conversion to ONNX Runtime for fast CPU inference.
  - *Verification:* ONNX CPU inference time $<120\text{ms}$ per frame.

#### Day 19: RBAC & Input Security Hardening
- **Milin (`frontend/`):** Role-based navigation guards hiding authority views from citizens.
  - *Verification:* Logging in as Citizen hides authority navigation links.
- **Utkarsh (`backend/`):** FastAPI `require_roles` dependency injection.
  - *Verification:* Attempting admin endpoint with Citizen token returns HTTP 403.
- **Sankalp (`ai_engine/`):** File upload magic byte validation (`FF D8 FF` for JPEG, `89 50 4E 47` for PNG).
  - *Verification:* Non-image file disguised as `.jpg` is rejected with HTTP 400.

#### Day 20: Governance Audit Logging
- **Milin (`frontend/`):** Audit History tab inside Authority Detail view.
  - *Verification:* Tab renders chronological action log for ticket.
- **Utkarsh (`backend/`):** Immutable Audit Logger writing state changes to `audit_logs` table.
  - *Verification:* Status change inserts immutable log row.
- **Sankalp (`ai_engine/`):** Stress testing Celery worker queue under 50 simultaneous jobs.
  - *Verification:* Stress script completes with zero worker crashes.

#### Day 21: Phase 3 Weekly Integration Test
- **Team Integration:** Execute `tests/integration/test_phase3.py`.

---

### Phase 4: Production Tuning & Staging Deployment (Days 22–30)

- **Days 22–24:** UI micro-animations, PostGIS spatial index optimization, edge-case testing.
- **Days 25–27:** Docker Compose containerization (`Dockerfile` for Frontend, Backend, Celery).
- **Days 28–30:** Staging deployment (Vercel + Neon + Render), KPI dossier validation report, production readiness review.
