# Project Rules for RoadRuler Repository

## 🚨 MANDATORY AUTOMATED DOCUMENTATION DIRECTIVE

Every AI agent (Antigravity) working on this repository MUST strictly follow these rules on **EVERY prompt and task**:

### 1. Mandatory Post-Task Documentation & Git Activity Logging
After performing ANY code modification, bug fix, file edit, or Git operation (such as branch renaming/creation, pushing to remotes, opening PRs, or configuring repository protection rulesets):
- Identify the developer context based on the modified files or target domains:
  - `frontend/` $\rightarrow$ **Milin** (`docs/daily_log/milin/` & `docs/deliverables/individuals/milin/deliverables.md`)
  - `backend/` $\rightarrow$ **Utkarsh** (`docs/daily_log/utkarsh/` & `docs/deliverables/individuals/utkarsh/deliverables.md`)
  - `ai_engine/` $\rightarrow$ **Sankalp** (`docs/daily_log/sankalp/` & `docs/deliverables/individuals/sankalp/deliverables.md`)
- Append a timestamped markdown entry in `docs/daily_log/{developer}/YYYY-MM-DD.md` following the exact template in `.agents/skills/doc-logger/SKILL.md`.
- **Git operations and repository setup actions** must be explicitly logged under the developer whose domain is active or under the repository owner (Sankalp) as a distinct task entry, including all command logs and target links.
- Mark completed tasks in `docs/deliverables/individuals/{developer}/deliverables.md`.

### 2. Strict Anti-Fabrication & Production Quality
- **NEVER fabricate test results, metrics, or terminal command outputs.**
- Always run actual terminal commands and copy true execution outputs into the log files.
- Never use placeholder returns (`return True`), stub functions, or dummy API mock handlers in core production code.
- If a command or test fails, document the exact failure output and your step-by-step resolution/rollback.

