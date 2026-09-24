# Milin Kanu - Deliverables & Verification Checklist
**Domain:** Frontend UI / UX / Leaflet Maps / Clerk Auth / React  
**Working Directory:** `frontend/`

---

## Deliverables Checklist

### Phase 1: Core UI & Authentication (Days 1–7)
- [x] **Day 1:** Scaffolding Vite React app, TailwindCSS setup, base router (`/`, `/report`, `/track`, `/authority`, `/public`).
- [x] **Day 2:** Clerk React SDK integration, `<ClerkProvider>`, Login/Signup modals, `<ProtectedRoute />` component.
- [x] **Day 3:** Leaflet.js + OpenStreetMap `<LocationPickerMap />` with draggable marker & geolocation.
- [x] **Day 4:** `<ReportIssueForm />` component with photo upload preview, category dropdown, description, map location.
- [x] **Day 5:** `<ComplaintTracker />` fetches the signed-in citizen's report by ID and displays live status, AI category, severity, per-region detection class/confidence breakdown, location, evidence, and processing timeline.
- **Day 6: Submission feedback and API wiring**
  - [x] Toast loading, success, and error feedback with `react-hot-toast`; the submit button disables and shows progress immediately while the request is in flight.
- **Day 7: Frontend/backend integration**
  - [x] Vite proxy, Clerk bearer-token submission, and real API response handling are wired.
  - [ ] Interactive Clerk browser submission and tracking flow remains unverified. Backend submission through storage, database, and AI processing passed the integration suite.

### Phase 2: Deduplication UI & Authority Dashboard (Days 8–14)
- [x] **Day 8:** Nearby complaints map rendering (yellow pins) within 50m radius of selected pin — implemented, production build passes, and the report map renders in the local app.
- [x] **Day 9:** `<DuplicateWarningModal />` compares photos and lets the user support the nearby ticket or submit a separate report.
- [x] **Day 10:** `/authority` dashboard uses the protected queue API, live queue metrics, severity/status filters, and pagination.
- [x] **Day 11:** Toggleable `leaflet.heat` overlay renders API hotspot GeoJSON with cluster detail markers.
- [x] **Day 12:** `<ComplaintActionModal />` advances the allowed status, captures contractor/notes, uploads required resolution evidence, and refreshes the queue.
- [x] **Day 13:** Authority toolbar supports ID/details search, ward, category, severity, status, and SLA filters.
- [x] **Day 14:** Phase 2 API integration, frontend production build, and lint verification pass; interactive real-Clerk browser workflow remains unverified.
- [x] **Admin profile console:** Existing Admin demo profile can open `/admin`; verified Clerk Admin profiles see the shared live operations dashboard. Live API data still requires backend-verified Clerk authorization.
- [x] **Admin demo preview:** Local AI Admin quick login displays clearly labeled sample queue and hotspot data in read-only mode; live records and actions still require verified Clerk Admin authorization.

### Phase 3: Auto-Routing UI, Escalation & Transparency (Days 15–21)
- [ ] **Day 15:** Department Ownership Badge on complaint cards.
- [ ] **Day 16:** SLA Countdown Timer on authority task cards.
- [ ] **Day 17:** Public Transparency Portal homepage `/public`.
- [ ] **Day 18:** Notification Bell dropdown in header.
- [ ] **Day 19:** Role-based navigation guards hiding authority views from citizens.
- [ ] **Day 20:** Audit History tab inside Authority Complaint detail view.
- [ ] **Day 21:** Phase 3 End-to-End integration test pass.

### Phase 4: Polish & Deployment (Days 22–30)
- [ ] **Days 22–24:** UI micro-animations, glassmorphism dark-mode polish, mobile responsiveness tuning.
- [ ] **Days 25–27:** Production build optimization & Dockerfile creation.
- [ ] **Days 28–30:** Vercel staging deployment & demo presentation preparation.
