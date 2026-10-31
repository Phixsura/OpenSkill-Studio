# ADR-017 — AI Trust, Safety & Assurance Plane

**Status:** Accepted  
**Date:** 2026-11-01  
**Relates to:** ADR-006 (AI Evaluation), ADR-009 (Skill Pack Registry), ADR-010 (Workflow Packs), ADR-011 (Provider Capability), ADR-014 (SaaS Commercialization), ADR-016 (Developer Platform), Issue #52

## Context

OpenSkill Studio's AI-powered workflows, third-party apps, provider/model adapters, externally sourced components, assessments and federated artifacts create a risk surface that requires evidence-backed governance. Operational policy and reliability alone do not provide a lifecycle for deciding whether an AI capability is safe and appropriate.

This ADR establishes a product-level **AI Trust, Safety & Assurance Plane** that integrates with existing benchmark, experimentation, audit, extension and operations systems.

## Decision

### Architecture: `app/trustplane/` Package

Follow the `app/controlplane/` isolation pattern:

- New package `app/trustplane/` with `models/`, `services/`, `schemas/`, `api/`, `facade.py`
- Product code imports **only** through `app.trustplane.facade` — never directly from trust models/services
- `trust_` table prefix (mirrors `cp_` for control plane)
- Can be disabled for self-hosted deployments without touching product code

### Phase 1: AI System Inventory & Risk Classification (Parts A, B)

#### Tables

| Table | Purpose |
|-------|---------|
| `trust_ai_systems` | Canonical record for every governed AI capability |
| `trust_ai_system_uses` | Intended and prohibited use cases per system |
| `trust_risk_scoring_policies` | Configurable, versioned risk dimensions and tier thresholds |
| `trust_risk_assessments` | Append-only versioned risk assessments with separation of duty |
| `trust_audit_events` | Immutable audit trail (mirrors `cp_audit_events`) |

#### Enums

- `SystemType`: workflow_pack, developer_app, provider_binding, evaluation_pipeline, skill_pack, custom
- `SystemLifecycle`: draft → intake → under_review → approved → deployed → monitoring → paused → deprecated → retired
- `RiskTier`: minimal, low, medium, high, critical
- `UseType`: intended, prohibited
- `AssessmentStatus`: draft, submitted, approved, rejected, superseded

#### Key Design Decisions

1. **JSONB dimension scores** — scoring dimensions are configurable per policy, not hardcoded columns. An org can add domain-specific dimensions without schema changes.

2. **Append-only assessments** — new assessment = new row. Previous approved assessments are superseded on new approval. Full history preserved.

3. **Separation of duty** — DB-level CHECK constraint: `assessed_by != reviewed_by OR reviewed_by IS NULL`. Authors cannot approve their own risk assessments.

4. **Risk tier denormalization** — `trust_ai_systems.risk_tier` is set from the latest approved assessment's `effective_tier` for fast filtering and display.

5. **Loose entity coupling** — `linked_entity_type` + `linked_entity_id` reference other domain objects (workflow packs, developer apps, etc.) without FK constraints, so trust records survive entity deletion.

6. **Configurable tier thresholds** — weighted score → tier mapping is per-policy, not global constants. Platform seeds an 8-dimension default policy.

7. **Frozen audit registry** — `TRUST_AUDIT_ACTIONS` frozenset prevents action-name drift. Every `record_trust_audit` call validates against the registry.

#### API Surface

All endpoints org-scoped under `/api/v1/orgs/{org_id}/trust/...`:

- Systems: CRUD, lifecycle transitions, entity linking
- Use Cases: CRUD (delete blocked on deployed/monitored systems)
- Assessments: create → submit (computes score) → approve/reject (separation of duty)
- Policies: list, create (auto-deactivates previous)
- Audit Log: filterable event history

### Future Phases (outlined, not yet implemented)

| Phase | Parts | Key Tables |
|-------|-------|------------|
| 2 | C, H — Evidence Graph & Human Oversight | `trust_assurance_cases`, `trust_evidence_items`, `trust_evidence_links`, `trust_review_requests`, `trust_review_decisions` |
| 3 | D — Release & Install Gates | `trust_assurance_profiles`, `trust_gate_checks`, `trust_gate_results` |
| 4 | F — Runtime Guardrails | `trust_guardrail_policies`, `trust_guardrail_evaluations`, `trust_action_boundaries` |
| 5 | I, J — Monitoring & Incidents | `trust_monitors`, `trust_monitor_alerts`, `trust_incidents`, `trust_incident_actions` |
| 6 | L, M, N — Enterprise Templates & Reporting | `trust_governance_templates`, `trust_compliance_reports`, `trust_tenant_policies` |

### Integration Points

- **Provider execution** (ADR-011): Trust checks at the `execute()` call site for pre/post content validation
- **Pack approval** (ADR-009/010): Release gate checks before publishing to registry
- **App review** (ADR-016): Automated trust checks in the 8-step review pipeline
- **Evaluation pipeline** (ADR-006): AI evaluation results as evidence items
- **Experimentation** (#42): Experiment results as evidence; safety monitoring independent of experiment status
- **Control plane** (ADR-014): Entitlement-gated trust features; trust violations can trigger tenant suspension

## Consequences

- Every AI capability gets a canonical record with owner, risk tier, and lifecycle state
- Risk assessments produce auditable, evidence-backed tier classifications
- Separation of duty is enforced at the DB level, not just application logic
- The trust plane is isolated behind a facade, allowing independent evolution
- Future phases build on this foundation: evidence graphs reference systems, gates reference assessments, guardrails reference risk tiers
