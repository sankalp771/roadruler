# Detailed Daily Task Guidance — Milin Kanu (Frontend & UI)

**Developer:** Milin Kanu  
**Domain:** Frontend UI / UX / Leaflet Maps / Clerk Authentication / React  
**Working Directory:** `frontend/`

---

## Structure of Daily Guidance
Each day includes:
1. **Purpose:** Why this feature is being built and how it serves the civic platform.
2. **What to Do:** Detailed architectural and implementation steps.
3. **What to Expect:** Component behavior, state flow, and user interaction design.
4. **What to Check / Valid Output:** Exact verification tests, terminal commands, and valid visual/console outputs.

---

# Phase 1: Foundation, Auth & Citizen Reporting (Days 1–7)

## Day 1: Project Scaffolding, Design System & Routing
* **Purpose:** Establish a production-grade, fast React application foundation with a modern design system (Inter font, dark mode capability, clean CSS tokens) and scalable client-side routing.
* **What to Do:**
  1. Execute `npm create vite@latest frontend -- --template react`.
  2. Install dependencies: `npm install react-router-dom lucide-react clsx tailwindmerge axios`.
  3. Setup TailwindCSS / Vanilla CSS tokens for background (`#0B0F19`), surface (`#111827`), primary (`#3B82F6`), critical hazard (`#EF4444`), moderate (`#F59E0B`), and success (`#10B981`).
  4. Create route structure in `src/App.jsx`:
     - `/` $\rightarrow$ Landing / Home View
     - `/report` $\rightarrow$ Citizen Report Submission Form
     - `/track` $\rightarrow$ Real-time Ticket Status Lookup
     - `/authority` $\rightarrow$ Authority Dashboard
     - `/public` $\rightarrow$ Public Transparency Analytics
* **What to Expect:** Clean, responsive navigation bar header with dark mode aesthetic and instant page transitions via React Router.
* **What to Check / Valid Output:**
  ```bash
  cd frontend
  npm run build
  ```
  *Output requirement:* `dist/` created with 0 lint or build warnings. Opening `http://localhost:5173` renders clean home view with working navigation links.

---

## Day 2: Clerk Authentication Integration & Route Protection
* **Purpose:** Secure citizen and authority user sessions with enterprise-grade authentication (Google OAuth, Email OTP) so reports can be audited and linked to real users.
* **What to Do:**
  1. Install `@clerk/clerk-react`.
  2. Create `.env.local` containing `VITE_CLERK_PUBLISHABLE_KEY=pk_test_...`.
  3. Wrap root application in `ClerkProvider` inside `src/main.jsx`.
  4. Build `<Navbar />` with Clerk UI components: `<SignedIn>`, `<SignedOut>`, `<UserButton />`, `<SignInButton />`.
  5. Build reusable `<ProtectedRoute />` component in `src/components/ProtectedRoute.jsx` that checks `useAuth()` status and redirects unauthenticated users to sign-in.
* **What to Expect:** Clicking "Sign In" opens Clerk's modal. Authenticated user profile picture appears in the navbar; navigating to `/report` without auth forces sign-in.
* **What to Check / Valid Output:**
  - `console.log(useAuth())` returns valid `userId` and `getToken()` function.
  - Manual test: Unauthenticated navigation to `/report` redirects to sign-in screen.

---

## Day 3: Interactive Geolocation Map Picker Component
* **Purpose:** Enable citizens to pin the exact geographic location of a road hazard on an interactive map, replacing inaccurate text addresses.
* **What to Do:**
  1. Install `leaflet` and `react-leaflet`. Import Leaflet CSS in `src/index.css`.
  2. Create `src/components/LocationPickerMap.jsx`:
     - Render `MapContainer` centered on default city coordinates (e.g. Mumbai: `19.0760, 72.8777`).
     - Render custom draggable `Marker` with custom Leaflet SVG pin icon.
     - Add "Locate Me" button triggering `navigator.geolocation.getCurrentPosition()`.
     - Update parent form state `{ latitude, longitude }` on marker `dragend` or map click.
* **What to Expect:** Smooth, responsive map tile rendering using OpenStreetMap tiles. Dragging the pin continuously updates lat/lng coordinates in the UI.
* **What to Check / Valid Output:**
  - Verify lat/lng coordinates update to 6 decimal places (e.g. `19.218321, 72.873145`).
  - Browser console logs `{ lat: 19.218321, lng: 72.873145 }` on marker placement.

---

## Day 4: Citizen Report Submission Form UI
* **Purpose:** Provide a seamless, friction-free reporting experience allowing citizens to upload road damage photos, select hazard categories, and attach location data.
* **What to Do:**
  1. Build `src/pages/ReportIssue.jsx`.
  2. Components:
     - Drag & Drop photo upload zone with image preview and file size validation ($<10\text{MB}$).
     - Category dropdown: `POTHOLE`, `WATERLOGGING`, `BROKEN_STREETLIGHT`, `DAMAGED_SURFACE`, `TRAFFIC_HAZARD`.
     - Description textarea.
     - Embedded `<LocationPickerMap />`.
     - Submit button with loading spinner during upload.
  3. Wire to backend using `axios.post('/api/v1/complaints', formData, { headers: { 'Content-Type': 'multipart/form-data' } })`.
* **What to Expect:** Selecting an image displays a thumbnail preview immediately. Tapping Submit sends `FormData` and shows a progress bar.
* **What to Check / Valid Output:**
  - Submit request sends HTTP POST payload with keys `file`, `latitude`, `longitude`, `category`, `description`.
  - On HTTP 201 response, redirects to `/track?id=<complaint_id>`.

---

## Day 5: Complaint Status Tracker & Timeline View
* **Purpose:** Deliver transparency to citizens by showing their report's progress, AI detection severity tags, and authority resolution updates.
* **What to Do:**
  1. Build `src/pages/TrackComplaint.jsx`.
  2. Implement URL query parameter lookup (`?id=XYZ`).
  3. Design `<StatusTimeline />` component rendering steps:
     - `1. Report Submitted` $\rightarrow$ `2. AI Analyzed (Severity Tagged)` $\rightarrow$ `3. Assigned to Authority` $\rightarrow$ `4. Repair In Progress` $\rightarrow$ `5. Resolved`.
  4. Render AI evidence badge (e.g., `CRITICAL SEVERITY (Score: 88/100) - Pothole Detected`).
* **What to Expect:** Inputting a valid complaint ID fetches and renders full status history, image evidence, and location marker on a read-only map.
* **What to Check / Valid Output:**
  - Fetch request `GET /api/v1/complaints/{id}` returns HTTP 200 with complete JSON status model.
  - UI correctly shifts active step highlight based on status string.

---

## Day 6: Optimistic UI & Toast Notifications
* **Purpose:** Improve perceived performance and user confidence through instantaneous UI feedback.
* **What to Do:**
  1. Install `react-hot-toast`. Add `<Toaster />` to root `App.jsx`.
  2. Implement optimistic state updates in `<ReportIssueForm />`:
     - Immediately disable form and trigger toast `toast.loading("Analyzing photo & logging report...")`.
     - Update toast on success: `toast.success("Report registered successfully!")`.
     - On error: `toast.error("Failed to submit report. Please retry.")`.
* **What to Expect:** Non-blocking, smooth toast pop-ups giving clear operational status.
* **What to Check / Valid Output:**
  - Submitting form triggers notification toast instantly without UI freezing.

---

## Day 7: Phase 1 Integration Test Pass
* **Purpose:** Validate complete frontend flow with Utkarsh's backend and Sankalp's AI engine.
* **What to Do:**
  1. Run end-to-end user workflow test: Sign in with Clerk $\rightarrow$ Navigate to `/report` $\rightarrow$ Upload test pothole image $\rightarrow$ Pin Thakur College on map $\rightarrow$ Submit $\rightarrow$ Verify redirection to `/track`.
* **What to Expect:** Whole submission lifecycle completes seamlessly with real data saved to Neon DB.
* **What to Check / Valid Output:**
  - Zero browser console errors.
  - Integration test suite passes 100%.

---

# Phase 2: Deduplication UI, Authority Dashboard & Heatmaps (Days 8–14)

## Day 8: Nearby Open Complaints Map Layer
* **Purpose:** Inform citizens of existing nearby complaints before they submit, preventing unnecessary duplicate tickets.
* **What to Do:**
  1. In `<LocationPickerMap />`, add an API call to `GET /api/v1/complaints/nearby?lat=X&lng=Y&radius=50` whenever the pin is moved.
  2. Render nearby complaints as distinct yellow pin markers.
  3. Clicking a yellow marker opens a popup preview showing the existing complaint photo and status.
* **What to Expect:** Moving the pin near an existing issue displays nearby yellow markers on the map.
* **What to Check / Valid Output:**
  - Map queries API and renders yellow pins within 50m radius accurately.

---

## Day 9: "Duplicate Detected — Upvote Instead" Modal
* **Purpose:** Convert duplicate submissions into upvotes on existing tickets, saving municipal resources.
* **What to Do:**
  1. Build `src/components/DuplicateWarningModal.jsx`.
  2. When the backend or spatial search detects a duplicate match, pop up the modal displaying:
     - Side-by-side comparison of user's photo vs existing reported photo.
     - Button: *"Upvote & Support Existing Ticket"*.
     - Button: *"File as New Separate Issue"*.
  3. Wiring: "Upvote" sends `POST /api/v1/complaints/{id}/upvote` and redirects to that ticket's tracking page.
* **What to Expect:** Smooth modal popup giving citizens clear choices when a duplicate is found.
* **What to Check / Valid Output:**
  - Upvoting calls upvote API and increments upvote count without creating a duplicate database row.

---

## Day 10: Authority Dashboard Core Layout & Queue Table
* **Purpose:** Provide Ward Officers and PWD admins with a high-density, actionable dashboard to review and prioritize incoming reports.
* **What to Do:**
  1. Build `src/pages/AuthorityDashboard.jsx`.
  2. Components:
     - Top Stat Cards: `Total Active`, `Critical Hazards`, `Avg SLA Response Time`, `Resolved This Week`.
     - Filterable Data Table: Columns: `ID`, `Photo`, `Category`, `Severity Badge`, `Location/Ward`, `SLA Status`, `Actions`.
  3. Fetch data via `GET /api/v1/authority/complaints`.
* **What to Expect:** High-density, professional admin view displaying priority-sorted tickets.
* **What to Check / Valid Output:**
  - Data table renders severity badges (`CRITICAL` in red, `MODERATE` in orange, `MINOR` in blue).

---

## Day 11: Geospatial Hotspot Heatmap Overlay
* **Purpose:** Visualize high-density hazard areas so authorities can contract major road resurfacing instead of minor patches.
* **What to Do:**
  1. Install `leaflet.heat` or `react-leaflet-heatmap-layer`.
  2. Add Heatmap toggle switch on Authority Map.
  3. Fetch GeoJSON from `GET /api/v1/analytics/hotspots`.
  4. Render red/yellow gradient heatmap intensity layer based on complaint density.
* **What to Expect:** Map displays vibrant red heat blobs over high-density complaint clusters.
* **What to Check / Valid Output:**
  - Heatmap layer toggles on/off smoothly; gradient intensity matches cluster density.

---

## Day 12: Authority Action & Work Order Modal
* **Purpose:** Allow Ward Officers to update ticket status, assign repair contractors, and upload resolution proof.
* **What to Do:**
  1. Build `src/components/ComplaintActionModal.jsx`.
  2. Form fields:
     - Status Selector (`PENDING`, `ASSIGNED`, `IN_REPAIR`, `RESOLVED`).
     - Contractor Name input.
     - Officer Notes textarea.
     - Resolution Photo upload input (for `RESOLVED` status).
  3. Send update via `PATCH /api/v1/authority/complaints/{id}/status`.
* **What to Expect:** Modal opens on clicking any table row action button; submitting updates table instantly.
* **What to Check / Valid Output:**
  - Patch request updates complaint status and triggers optimistic UI table refresh.

---

## Day 13: Search, Multi-Filter Toolbar & Ward Analytics
* **Purpose:** Enable officers to quickly search and filter thousands of records by ward, hazard type, or severity.
* **What to Do:**
  1. Build `<FilterBar />` with dropdowns: `Ward Filter`, `Hazard Category`, `Severity Level`, `SLA State`.
  2. Add text search input for Complaint ID or address keyword.
  3. Update query parameters and re-fetch queue data seamlessly.
* **What to Expect:** Selecting filters instantly filters table rows without full page reloads.
* **What to Check / Valid Output:**
  - Selecting "Ward 4" + "Critical" sends `GET /api/v1/authority/complaints?ward_id=4&severity=CRITICAL` returning matching subset.

---

## Day 14: Phase 2 Integration Test Pass
* **Purpose:** Verify complete deduplication, heatmap rendering, and authority workflow integration.
* **What to Do:**
  1. Perform full end-to-end test of upvoting, heatmap display, status changes, and filter toolbar.
* **What to Check / Valid Output:**
  - Zero console errors; 100% integration test pass.

---

# Phase 3: Auto-Routing UI, SLA Countdown & Public Portal (Days 15–21)

## Day 15: Department Routing Badge Display
* **Purpose:** Display which municipal department (PWD, Local Ward, Traffic Police) owns each ticket.
* **What to Do:**
  1. Update complaint cards and detail views to render Department Badges:
     - `PWD (Arterial Roads)` $\rightarrow$ Blue Badge
     - `Ward Local Maintenance` $\rightarrow$ Green Badge
     - `Traffic Police Safety` $\rightarrow$ Orange Badge
* **What to Expect:** Clear visual indication of responsible agency on every complaint card.
* **What to Check / Valid Output:**
  - Card displays correct department badge based on backend JSON response.

---

## Day 16: SLA Countdown Timer Component
* **Purpose:** Create urgency for municipal officers to resolve critical hazards before SLA breach.
* **What to Do:**
  1. Build `src/components/SLATimer.jsx`.
  2. Calculate remaining time: $\text{Deadline} - \text{Current Time}$.
  3. Dynamic Styling:
     - $>50\%$ time left $\rightarrow$ Green badge.
     - $<25\%$ time left $\rightarrow$ Flashing Amber.
     - Breached / Escalated $\rightarrow$ Flashing Red "ESCALATED" badge.
* **What to Expect:** Live counting-down timer updating every second on active tickets.
* **What to Check / Valid Output:**
  - Timer updates in real time; breached tickets display bold red `ESCALATED` label.

---

## Day 17: Public Transparency Portal Homepage (`/public`)
* **Purpose:** Build public trust by showcasing live city-wide resolution statistics, authority response rates, and fixed issues.
* **What to Do:**
  1. Build `src/pages/PublicPortal.jsx`.
  2. Sections:
     - Hero Stats Banner: Total Reported, Total Fixed (%), Average Resolution Time (Days).
     - Ward Performance Leaderboard table (ranking wards by resolution speed).
     - Live "Recently Fixed" photo carousel showing Before & After repair pictures.
  3. Fetch data from `GET /api/v1/public/stats`.
* **What to Expect:** Beautiful, publicly accessible dashboard with responsive charts and metrics.
* **What to Check / Valid Output:**
  - Accessible without authentication; metrics populate from backend cache.

---

## Day 18: Notification Center Component
* **Purpose:** Keep citizens informed when their reported road issue is assigned, under repair, or fixed.
* **What to Do:**
  1. Build `<NotificationBell />` component in header.
  2. Dropdown listing unread status notifications (e.g., *"Your pothole report #104 status updated to IN REPAIR"*).
  3. Tapping notification marks it read and navigates to tracking page.
* **What to Expect:** Red notification badge showing unread count; clicking opens notification list.
* **What to Check / Valid Output:**
  - Clicking notification updates unread counter badge dynamically.

---

## Day 19: Role-Based Access Control (RBAC) UI Guards
* **Purpose:** Prevent citizens from accessing internal authority administrative tools.
* **What to Do:**
  1. Build `src/components/RoleGuard.jsx` inspecting user metadata roles from Clerk (`user.publicMetadata.role`).
  2. Wrap `/authority` routes in `<RoleGuard allowedRoles={['WARD_OFFICER', 'ADMIN']}>`.
  3. Show friendly 403 Access Denied view for unauthorized users.
* **What to Expect:** Regular citizens navigating to `/authority` see access restriction notice.
* **What to Check / Valid Output:**
  - Citizen user redirected away from `/authority`; Ward Officer granted clean access.

---

## Day 20: Governance Audit History Timeline Tab
* **Purpose:** Ensure accountability by displaying an unalterable history of every action taken on a ticket.
* **What to Do:**
  1. Inside complaint detail modal, add `<AuditTrailTab />`.
  2. Display chronological vertical timeline:
     - `10:14 AM - Created by Citizen (Milin K.)`
     - `10:15 AM - AI Analyzed: CRITICAL Pothole`
     - `11:30 AM - Assigned to Officer Sharma (Ward 3)`
     - `02:00 PM - Status changed to IN_REPAIR`
* **What to Expect:** Clean, timestamped audit log showing every system and officer event.
* **What to Check / Valid Output:**
  - Audit tab renders complete event sequence fetched from backend audit log.

---

## Day 21: Phase 3 Integration Test Pass
* **Purpose:** Validate complete routing, SLA tracking, notifications, public portal, and security controls.
* **What to Do:**
  1. Run end-to-end integration test suite.
* **What to Check / Valid Output:**
  - Zero console errors; 100% pass on integration suite.

---

# Phase 4: Production Polish & Staging Deployment (Days 22–30)

## Days 22–24: UI Micro-Animations & Dark Mode Refinement
* **Purpose:** Polish UI/UX to a commercial, production-ready standard.
* **What to Do:** Add smooth hover transitions, glassmorphism cards (`backdrop-blur-md`), dark mode styling, and skeleton loading shimmer effects.

## Days 25–27: Production Build Optimization & Dockerization
* **Purpose:** Package frontend for cloud deployment.
* **What to Do:** Create `frontend/Dockerfile` using multi-stage Nginx build. Run `npm run build` and ensure bundle size $<500\text{KB}$ gzipped.

## Days 28–30: Vercel Staging Deployment & Live Demo
* **Purpose:** Deploy live staging environment for public demo and academic review.
* **What to Do:** Deploy frontend to Vercel, connect production domain, verify HTTPS, and complete final end-to-end smoke test.
