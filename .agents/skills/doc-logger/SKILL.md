---
name: doc-logger
description: Enforces detailed change logging, real test verification, project context awareness, and strict anti-fabrication rules for all agents working on the RoadRuler repository.
---

# Skill: RoadRuler Production Documentation & Change Logger

## Project Context
**Project Name:** Crowdsourced Road Issue Reporter (`RoadRuler`)  
**Domain:** AI-Enhanced Civic Technology / Urban Infrastructure / Computer Vision  
**Target:** Production-Grade Marketable Civic Platform  
**Team & Domains:**
- **Milin Kanu (`frontend/`):** Vite + React, Leaflet.js / OpenStreetMap, Clerk Authentication, Responsive UI, Citizen & Authority UX.
- **Utkarsh Mishra (`backend/`):** FastAPI, SQLAlchemy, Neon PostgreSQL + PostGIS, Clerk JWT Authentication, Routing & SLA Escalation Engine.
- **Sankalp Pandey (`ai_engine/`):** PyTorch + YOLOv8 road damage detection, OpenCV pre-processing, ResNet50 visual embedding generator, Cosine Similarity deduplication engine, DBSCAN spatial hotspot clustering.

---

## Strict Rules & Anti-Fabrication Constraints

1. **PRODUCTION-GRADE QUALITY (NO SHORTCUTS):**
   - Never write placeholder returns (e.g., `return True`), stub functions, or dummy API handlers in core logic.
   - Code must be modular, fully typed, include proper exception handling (`try/except` with explicit HTTP error status codes), and use input validation models (Pydantic).

2. **ANTI-FABRICATION DIRECTIVE:**
   - NEVER fabricate test outputs, log data, or benchmark numbers.
   - ALWAYS execute terminal commands, run real tests, and paste true execution logs into daily log files.
   - If a command or test fails, document the exact failure output and your step-by-step resolution/rollback.

3. **MANDATORY LOGGING WORKFLOW:**
   Whenever you complete or modify any code on behalf of a developer (**Milin**, **Utkarsh**, or **Sankalp**):

   **Step A:** Identify the developer based on the file paths modified:
   - `frontend/` $\rightarrow$ **Milin**
   - `backend/` $\rightarrow$ **Utkarsh**
   - `ai_engine/` $\rightarrow$ **Sankalp**

   **Step B:** Append a timestamped entry to `docs/daily_log/{developer}/YYYY-MM-DD.md` using the exact format below:

   ```markdown
   ## [<HH:MM:SS>] Task: <Task Description>

   ### 1. Objective & Architectural Rationale
   - Clear explanation of the feature/change and design choice.

   ### 2. Files Modified / Created
   - [`path/to/file.ext`](file:///d:/roadruler/path/to/file.ext#L1-L50)

   ### 3. Implementation Details
   - Technical breakdown of logic implemented.

   ### 4. Terminal Commands & Actual Test Output
   ```bash
   # Exact command run
   $ <command>
   ```
   **Output:**
   ```
   <TRUE TERMINAL OUTPUT HERE - DO NOT FABRICATE>
   ```

   ### 5. Errors Encountered & Resolution / Rollbacks
   - Description of any errors encountered and how they were resolved.

   ### 6. Verification Status
   - [x] Verified working with true test execution.
   ```

   **Step C:** Update the respective developer's deliverable checklist in `docs/deliverables/individuals/{developer}/deliverables.md`.
