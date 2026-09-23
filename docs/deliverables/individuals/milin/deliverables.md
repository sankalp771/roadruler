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
- [ ] **Day 8:** Nearby complaints map rendering (yellow pins) within 50m radius of selected pin.
- [ ] **Day 9:** `<DuplicateWarningModal />` prompting user to upvote existing ticket.
- [ ] **Day 10:** Authority Dashboard layout `/authority` with metrics cards, sidebar, filterable table.
- [ ] **Day 11:** Heatmap Layer on Leaflet map using `leaflet.heat`.
- [ ] **Day 12:** `<ComplaintActionModal />` for status updates, contractor assignment, and notes.
- [ ] **Day 13:** Multi-parameter Search & Filter Toolbar.
- [ ] **Day 14:** Phase 2 End-to-End integration test pass.

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
