# ADR-018 — Global Autonomous Operations & Governance Plane

**Status:** Accepted  
**Date:** 2026-11-01  
**Relates to:** ADR-014 (SaaS Commercialization), ADR-017 (AI Trust & Safety), Issue #46

## Context

Federation enables a network of independent deployments. Operating large deployments and federated networks reliably across regions, providers, and tenants requires a dedicated operations/governance plane capable of maintaining SLOs, cost boundaries, regulatory policies, and disaster recovery at scale.

This ADR establishes a **Global Operations & Governance Plane** that integrates with existing billing, workflow, experimentation, ecosystem intelligence, integration, and federation systems.

## Decision

### Architecture: `app/opsplane/` Package

Follow the same facade-isolated pattern as `app/controlplane/` and `app/trustplane/`:

- New package `app/opsplane/` with `models/`, `services/`, `api/`, `facade.py`
- `ops_` table prefix
- Platform-admin-gated API endpoints under `/api/v1/platform/ops/`

### Models (22 tables across 3 model files)

#### Infrastructure (`models/infrastructure.py`) — Parts A, B, D
- `ops_deployment_regions` — multi-region with provider/status/primary designation
- `ops_runtime_cells` — per-region cells with capacity and tenant assignment
- `ops_service_instances` — versioned services with health checks
- `ops_routing_rules` — workload placement with conditions and weights
- `ops_metric_samples` — observability metric samples (append-only)

#### Reliability (`models/reliability.py`) — Parts C, E, F, I, L
- `ops_slo_definitions` — SLI/target/error-budget with sliding windows
- `ops_incidents` — 7-state lifecycle (SEV1–SEV4), timeline, SLO impact
- `ops_detection_rules` — threshold/anomaly/composite with cooldown
- `ops_failover_records` — region failover with service/tenant migration
- `ops_recovery_plans` — DR plans with RTO/RPO and test results

#### Governance (`models/governance.py`) — Parts G, H, J, K, M, N, O, P, R, S
- `ops_policies` — policy-as-code with enforcement mode (enforce/audit)
- `ops_remediation_playbooks` — steps + rollback, blast-radius check, approval gate
- `ops_playbook_runs` — execution with 7-state lifecycle
- `ops_cost_records` — AI FinOps with 7 cost categories per provider/region
- `ops_cost_budgets` — budget alerts with configurable thresholds
- `ops_capacity_forecasts` — projected usage with confidence levels
- `ops_compliance_evidence` — framework/control evidence snapshots
- `ops_retention_policies` — data retention/deletion orchestration
- `ops_change_records` — change management with risk/approval
- `ops_governance_approvals` — target-scoped approval records
- `ops_game_days` — chaos testing with plan/results/lessons
- `ops_healing_actions` — human-supervised self-healing with blast radius preview

### Key Design Decisions

1. **Platform-scoped, not org-scoped** — operations plane manages platform infrastructure, unlike trustplane which is org-scoped
2. **Human-supervised self-healing** — healing actions default to `requires_human_approval=True`; automation proposes, humans approve
3. **Blast-radius checks** — playbooks and healing actions include blast-radius preview before execution
4. **Policy enforcement modes** — `enforce` (block violations) vs `audit` (log only) for gradual rollout
5. **Error budget tracking** — SLOs track remaining error budget for data-driven reliability decisions
6. **Append-only metrics** — `ops_metric_samples` is write-only for audit trail

## Consequences

- Platform operators can manage multi-region deployments with SLO-driven reliability
- AI FinOps provides cost visibility and budget controls across providers
- Policy-as-code enables consistent governance across regions and tenants
- Self-healing automation bounded by human approval and blast-radius checks
- Chaos testing (game days) validates recovery plans before real incidents
