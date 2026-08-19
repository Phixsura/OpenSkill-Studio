# OpenSkill Studio — Cohort Operations, Client Briefs & Multimodal AI Evaluation (ADR-008)

> Status: **Implemented** | Author: Lyphixia Wang | Date: 2026-08-17
> Depends on: ADR-001 through ADR-007
> Implements: Issue #16

---

## 1. Context

OpenSkill Studio has a complete AI-creator workflow: skills, projects, structured media deliverables, prompts, generation metadata, peer/AI review, and portfolio. The platform needed an **operational layer** to run real training programs and commercial production work.

Three gaps were identified:
1. **No cohort/class management** — organizations couldn't segment learners into training groups
2. **No commercial workflow** — no way to introduce real client briefs and route production work
3. **Text-only AI evaluation** — the evaluator couldn't see image/video submissions

## 2. Design Decisions

### 2.1 Cohort as a first-class entity (not folder/tag)

A `Cohort` is an org-scoped entity with its own lifecycle (draft → active → completed → archived), membership, and content assignments. This was chosen over tag-based grouping because:
- Cohorts have scheduling (start_date, end_date, deadline overrides)
- Membership has roles (learner/instructor) distinct from org roles
- Visibility rules need a clear boundary ("is user in this cohort?")

### 2.2 Backward-compatible visibility

Content visibility uses a three-source model:
- **Org-wide**: projects/skills with no cohort or creator assignment (existing behavior)
- **Cohort-assigned**: via `CohortProjectAssignment` / `CohortSkillAssignment`
- **Individually assigned**: via `ProjectCreatorAssignment`

Students see union(org-wide, my-cohorts, assigned-to-me). Instructors see everything. This preserves backward compatibility: organizations without cohorts work exactly as before.

### 2.3 Override precedence

Submission timing follows: personal extension > cohort override > project default. Same for max_submissions. This lets instructors set org-wide defaults and per-cohort exceptions without duplicating projects.

### 2.4 Client Brief → Project conversion

Briefs are a separate entity (not a project subtype) because they represent client requirements, not instructor assignments. The `convert_to_project()` flow creates a real Project with deliverables from the brief's specs, links them via `client_brief_id` FK, and reuses the entire existing submission/review pipeline.

### 2.5 Multimodal LLM client

The `complete()` method now accepts `str | list` for `user_prompt`. The Anthropic block format is canonical; `_to_openai_content()` translates for OpenAI. This is fully backward-compatible — existing text-only callers pass `str` and get identical behavior.

### 2.6 Video evaluation via frame sampling

Direct video input to LLMs is unreliable/unsupported by most providers. We use deterministic ffmpeg frame sampling: `N` frames at positions `duration * i / (N + 1)`. Metadata records the strategy so evaluators can disclose limitations. Temp files are cleaned in `finally` blocks.

## 3. Database Schema

### New tables
| Table | Purpose |
|-------|---------|
| `cohorts` | Training cohort/class |
| `cohort_members` | User enrollment with role |
| `cohort_skill_assignments` | Skills assigned to cohort |
| `cohort_project_assignments` | Projects assigned with deadline/limit overrides |
| `client_briefs` | Commercial production requests |
| `brief_applications` | Learner interest in commercial work |
| `project_creator_assignments` | Individual creator assignment to projects |

### Modified tables
- `projects`: added `client_brief_id` FK (SET NULL), `cohort_id` FK (SET NULL)
- `evaluation_tasks`: extended `eval_type` enum with `image_review`, `video_review`, `prompt_review`, `commercial_submission_review`

## 4. API Surface

35 new endpoints across 3 routers:
- `/orgs/{org_id}/cohorts/*` — CRUD, membership, assignment, dashboards
- `/orgs/{org_id}/briefs/*` — CRUD, convert, applications
- `/orgs/{org_id}/projects/{id}/creators/*` — individual assignment

## 5. Security

All endpoints follow existing RBAC patterns (`require_org_member`). Org-scoping is verified at every endpoint via `_verify_project_org`, `cohort.org_id != org_id`, or `brief.org_id != org_id`. Adversarial tests cover cross-org and cross-cohort ID confusion on every new resource type.

## 6. Testing

- 69 new integration tests (823 total, was 754)
- 21-step E2E test covering the full operational loop
- 11 adversarial isolation tests
- 15 multimodal eval unit tests with mock LLM/S3

---

*ADR-008 v1 — Cohort operations, client briefs, and multimodal AI evaluation.*
