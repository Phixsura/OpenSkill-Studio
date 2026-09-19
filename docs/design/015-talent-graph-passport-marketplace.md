# ADR-015: Verified Talent Graph, Skill Passport, Employment Marketplace & Workforce Intelligence

**Status**: Accepted (implemented in PR #33)
**Issue**: [#32 — Verified Talent Graph, Skill Passport, Employment Marketplace and Workforce Intelligence](https://github.com/Phixsura/OpenSkill-Studio/issues/32)
**Depends on**: ADR-002 (auth), ADR-003 (orgs), ADR-004 (skills), ADR-005 (projects), ADR-006 (eval), ADR-007 (portfolio), ADR-008 (cohorts), ADR-009 (packs), ADR-010 (workflows), ADR-011 (providers), ADR-012 (matching), ADR-013 (composers/talent), ADR-014 (SaaS control plane)

## Context

OpenSkill Studio spans learning → evaluation → commercial delivery → SaaS
commercialization, but lacks a **longitudinal talent layer** that:

1. Maintains a first-class, portable, evidence-backed model of what a person can do.
2. Closes the loop: learning → verified capability → employment → employer outcome → demand signal → curriculum improvement.

The existing `CapabilityTag` (ADR-011) is a workflow-level I/O taxonomy.
`CreatorCapabilityEvidence` (ADR-013) is per-org, tied to commercial
matching. `Certificate` (ADR-007) is a simple learning-path completion
record. None of these form a proper talent infrastructure.

This ADR introduces:

- **Capability Ontology** — hierarchical, lifecycle-managed, platform-level
- **Verified Evidence Ledger** — append-only, multi-source, provenance-backed
- **Capability Scoring** — derived, versioned, decay-aware
- **Skill Passport** — user-owned, privacy-controlled, verifiable snapshots
- **Assessments & Credentials** — blueprints, practical runs, rule-based issuance
- **Employer/Opportunity Model** — structured postings, capability requirements
- **Talent ↔ Opportunity Matching** — extends ADR-012 engine
- **Application/Placement Pipeline** — full lifecycle with audit
- **Internship/School Placement** — cohort exposure, supervision, employer verification
- **Outcome Tracking** — longitudinal events, alumni continuity
- **Workforce Intelligence** — demand/supply aggregation, gap analysis
- **Curriculum Intelligence** — coverage matrix, outcome analytics
- **Talent CRM** — consent-based pools, outreach
- **Privacy & Safety** — opt-in discoverability, protected-attribute exclusion

### Hard package boundary

All talent/employment code lives in `app/talent/{models,schemas,services,api}`,
following ADR-014's isolation pattern. Product code accesses talent via
`app.talent.facade`:

```python
# Facade exports — product code ONLY calls these
record_capability_evidence     # after skill completion, project approval, etc.
get_user_capability_profile    # derived scores for a user
get_passport_summary           # public passport view (respects privacy)
check_credential_status        # verify a credential is active
```

Talent code may import product **models** (User, Skill, Project, etc.),
never product **services**. The one exception: `services/evidence_ingest.py`
imports evaluation/project services for provenance resolution.

---

## Decision 1 — Capability Ontology (Issue §1–§3)

### Capability model

Elevate `CapabilityTag` into a full ontology node. The existing
`capability_tags` table stays (workflow I/O contracts), and a new
`capabilities` table represents the talent ontology:

```python
class Capability(Base):
    __tablename__ = "capabilities"

    id: Mapped[str] = ulid_pk()
    canonical_name: Mapped[str] = mapped_column(String(120), unique=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True)
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    # Top-level grouping: visual_design | production | communication |
    # workflow_design | ai_fundamentals | business
    category: Mapped[str] = mapped_column(String(40))
    parent_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("capabilities.id", ondelete="SET NULL"), nullable=True
    )
    # active | deprecated | merged | archived
    status: Mapped[str] = mapped_column(String(20), default="active", server_default="'active'")
    # When status=merged, points to the successor capability
    merged_into_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("capabilities.id", ondelete="SET NULL"), nullable=True
    )
    # Capability-family-specific level definitions override the platform default
    level_definitions: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # Decay configuration: half_life_days (NULL = no decay)
    decay_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_capabilities_category", "category"),
        Index("ix_capabilities_parent", "parent_id"),
        Index("ix_capabilities_status", "status"),
    )
```

### Capability relationships (§2)

```python
class CapabilityEdge(Base):
    __tablename__ = "capability_edges"

    id: Mapped[str] = ulid_pk()
    source_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("capabilities.id", ondelete="CASCADE")
    )
    target_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("capabilities.id", ondelete="CASCADE")
    )
    # requires | related_to | specializes | subsumes | commonly_paired_with
    edge_type: Mapped[str] = mapped_column(String(30))
    metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("uq_capability_edge", "source_id", "target_id", "edge_type", unique=True),
        Index("ix_capability_edges_target", "target_id"),
        # Prevent self-loops
        CheckConstraint("source_id != target_id", name="ck_no_self_loop"),
    )
```

**Graph validation**: A service-level validator runs on edge mutation:

- `requires` edges must not form cycles (bounded DFS, max depth 20).
- `subsumes` must be consistent with `parent_id` hierarchy (a parent
  subsumes children implicitly; explicit `subsumes` is for cross-branch
  relationships only).
- `specializes` must point from child → parent direction.

Validation rejects the write with 422 `CYCLE_DETECTED` or
`INCONSISTENT_HIERARCHY` and does NOT store the edge.

### Content-to-capability mappings (§3)

```python
class CapabilityMapping(Base):
    """Maps platform content (Skill, Pack, Project, etc.) to capabilities."""
    __tablename__ = "capability_mappings"

    id: Mapped[str] = ulid_pk()
    capability_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("capabilities.id", ondelete="CASCADE")
    )
    # skill | skill_pack | project_template | workflow_pack | rubric_criterion |
    # assessment_blueprint | commercial_project
    source_type: Mapped[str] = mapped_column(String(30))
    source_id: Mapped[str] = mapped_column(String(26))
    # 0.0–1.0: how much this source contributes to the capability
    contribution_weight: Mapped[float] = mapped_column(
        Numeric(3, 2), default=1.0, server_default="1.00"
    )
    # primary_instruction | practice | assessment | incidental
    evidence_type: Mapped[str] = mapped_column(String(30), default="primary_instruction")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("uq_cap_mapping", "capability_id", "source_type", "source_id", unique=True),
        Index("ix_cap_mapping_source", "source_type", "source_id"),
        CheckConstraint(
            "contribution_weight >= 0 AND contribution_weight <= 1",
            name="ck_contribution_weight_range"
        ),
    )
```

**Bridge to `CapabilityTag`**: A migration seeds initial `capabilities`
rows from existing `capability_tags` where appropriate (e.g.
`image_generation` → `AI Image Generation` capability). A
`capability_tag_id` nullable FK on `Capability` links to the workflow I/O
contract when one corresponds; they remain separate models because
the workflow taxonomy has a different lifecycle and contract semantics.

---

## Decision 2 — Verified Evidence Ledger (Issue §4–§6)

### Append-only evidence model

```python
class CapabilityEvidence(Base):
    """Append-only proof that a user demonstrated a capability."""
    __tablename__ = "capability_evidence"

    id: Mapped[str] = ulid_pk()
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE")
    )
    capability_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("capabilities.id", ondelete="CASCADE")
    )
    # skill_completion | exercise_result | assessment_result | project_approval |
    # rubric_score | peer_review | instructor_verification |
    # multimodal_ai_evaluation | commercial_project_approval | client_acceptance |
    # workflow_execution | credential | employment_verification
    source_type: Mapped[str] = mapped_column(String(40))
    source_id: Mapped[str] = mapped_column(String(26))
    org_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True
    )
    # Normalized to [0, 1]. NULL when binary (pass/fail).
    score_normalized: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    # System confidence in this evidence item [0, 1]
    confidence: Mapped[float] = mapped_column(Numeric(5, 4), default=1.0, server_default="1.0000")
    # self_reported | system_observed | peer_verified | instructor_verified |
    # client_verified | assessment_verified | employer_verified
    verification_level: Mapped[str] = mapped_column(String(30))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Immutability: corrections via supersede/void, never UPDATE.
    # Points to the evidence row this supersedes or voids.
    supersedes_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    # active | superseded | voided
    status: Mapped[str] = mapped_column(String(20), default="active", server_default="'active'")
    # Provenance, additional scores, rubric details, etc.
    metadata: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_evidence_user_cap", "user_id", "capability_id", "status"),
        Index("ix_evidence_source", "source_type", "source_id"),
        Index("ix_evidence_org", "org_id", "capability_id"),
        Index("ix_evidence_occurred", "user_id", "occurred_at"),
        # Idempotency: one active evidence per (user, capability, source_type, source_id)
        Index(
            "uq_evidence_idempotent",
            "user_id", "capability_id", "source_type", "source_id",
            unique=True,
            postgresql_where=text("status = 'active'"),
        ),
        CheckConstraint(
            "score_normalized IS NULL OR (score_normalized >= 0 AND score_normalized <= 1)",
            name="ck_evidence_score_range"
        ),
    )
```

**Immutability contract**: No UPDATE on `capability_evidence` except
`status` transitions: `active → superseded` (when a newer evidence for the
same source replaces it) or `active → voided` (when the source was
retracted). The new/corrected row is a fresh INSERT with
`supersedes_id` pointing to the old row.

A DB trigger (or service-level guard) rejects any UPDATE touching columns
other than `status`. The test suite asserts this invariant.

### Verification level weights (§5)

```python
VERIFICATION_WEIGHTS: dict[str, float] = {
    "employer_verified":    1.00,
    "client_verified":      0.95,
    "assessment_verified":  0.90,
    "instructor_verified":  0.85,
    "peer_verified":        0.70,
    "system_observed":      0.60,
    "self_reported":        0.30,
}
```

These weights feed into capability scoring (Decision 3). They are
versioned alongside the scoring algorithm — changes create a new scoring
config version. AI evaluations map to `system_observed` (weight 0.60),
never to instructor/client/employer tiers.

### Evidence provenance (§6)

Every evidence row has `source_type + source_id` tracing to the original
object. The service provides `get_evidence_provenance(evidence_id)` which
resolves the chain:

```
evidence → source record → parent record → ... → root
```

Example chain:

```json
{
  "evidence_id": "01J...",
  "chain": [
    { "type": "commercial_project_approval", "id": "01J...", "label": "AI Ad Project v2" },
    { "type": "submission", "id": "01J...", "label": "Final delivery" },
    { "type": "rubric_review", "id": "01J...", "label": "Instructor review 4.2/5" },
    { "type": "client_acceptance", "id": "01J...", "label": "Client accepted 2026-08-15" }
  ]
}
```

Authorization check: each link in the chain checks the requesting user's
read access. Links the user cannot see are replaced with
`{"type": "redacted", "reason": "insufficient_access"}`.

### Migration from `CreatorCapabilityEvidence` (ADR-013)

Existing `creator_capability_evidence` rows are migrated:

1. Each row maps `capability_key` → `capabilities.id` via the
   `CapabilityTag`→`Capability` bridge or a migration lookup table.
2. `evidence_type` maps to `source_type`; `weight` maps to
   `verification_level` (weight ≥ 0.9 → `instructor_verified`;
   0.6–0.89 → `peer_verified`; < 0.6 → `self_reported`).
3. The old table is retained read-only for 2 releases, then dropped.

The old `CreatorCapabilityEvidence` import path (creator matching service)
is redirected to write `capability_evidence` instead.

---

## Decision 3 — Capability Scoring and Decay (Issue §7–§9)

### Scoring algorithm (versioned)

```python
SCORING_VERSION = "1.0.0"

def compute_capability_score(
    evidence_rows: list[CapabilityEvidence],
    capability: Capability,
    now: datetime,
) -> CapabilityScore:
    """
    Algorithm v1.0.0:

    1. Filter: only status='active', non-expired evidence.
    2. For each evidence row, compute effective_score:
       - base = score_normalized (default 0.8 if NULL / binary pass)
       - verification_weight = VERIFICATION_WEIGHTS[verification_level]
       - freshness = decay(occurred_at, now, capability.decay_config)
       - effective = base × verification_weight × confidence × freshness
    3. Aggregate: Bayesian-shrunk mean (same formula as ADR-012 creator matching)
       shrunk = (n / (n + k)) × raw_mean + (k / (n + k)) × prior
       where k=3, prior=0.5
    4. Level = threshold lookup from capability.level_definitions or platform default.
    5. Confidence = 1 - (k / (n + k))  — reflects evidence volume.
    """
```

**Decay function** (§8):

```python
def decay(occurred_at: datetime, now: datetime, config: dict | None) -> float:
    """
    Exponential decay with configurable half-life.

    config = {"half_life_days": 365}   # slow decay (fundamentals)
    config = {"half_life_days": 90}    # fast decay (specific tool)
    config = None                      # no decay (soft skills)

    Formula: 2^(-age_days / half_life_days)
    """
    if config is None or "half_life_days" not in config:
        return 1.0
    age_days = (now - occurred_at).total_seconds() / 86400
    return 2 ** (-age_days / config["half_life_days"])
```

Evidence is **never deleted** by decay. Old evidence always contributes
_something_ — just less as it ages. A user with only stale evidence still
shows a non-zero (but low) score, clearly distinguishable from L0 (no
evidence).

### Level thresholds (§9)

Platform defaults (overridable per capability family via
`level_definitions`):

```python
DEFAULT_LEVEL_THRESHOLDS = {
    0: {"label": "No evidence",           "min_score": 0.00, "min_evidence": 0},
    1: {"label": "Foundation",            "min_score": 0.20, "min_evidence": 1},
    2: {"label": "Assisted practice",     "min_score": 0.40, "min_evidence": 3},
    3: {"label": "Independent production", "min_score": 0.60, "min_evidence": 5},
    4: {"label": "Commercial delivery",   "min_score": 0.75, "min_evidence": 8},
    5: {"label": "Expert / mentor",       "min_score": 0.90, "min_evidence": 12},
}
```

Level requires BOTH `min_score` AND `min_evidence`. A single perfect score
cannot reach L5. The `min_evidence` counts active, non-expired evidence
rows with verification_level ≥ `peer_verified`.

### Derived profile output

```json
{
  "capability_id": "01J...",
  "capability": "AI Product Visual Design",
  "level": 4,
  "score": 0.84,
  "confidence": 0.91,
  "evidence_count": 17,
  "last_verified_at": "2026-09-01T10:00:00Z",
  "verification_mix": {
    "client_verified": 4,
    "instructor_verified": 6,
    "system_observed": 7
  },
  "scoring_version": "1.0.0",
  "computed_at": "2026-09-13T08:00:00Z"
}
```

Profiles are computed on-demand (not materialized) to avoid staleness.
For list views and matching, a lightweight SQL aggregate produces level +
score without loading full evidence rows. A materialized view
(`mv_user_capability_summary`) is created for dashboard queries, refreshed
on a configurable schedule (default: hourly via arq worker).

---

## Decision 4 — Personal Skill Passport (Issue §10–§12)

### Passport model

```python
class SkillPassport(Base):
    """User-owned talent passport — one per user, metadata + privacy config."""
    __tablename__ = "skill_passports"

    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    # private | organization_only | share_link | public_subset
    default_visibility: Mapped[str] = mapped_column(
        String(20), default="private", server_default="'private'"
    )
    # Fields the user has chosen to expose externally (whitelist)
    # ["capabilities", "credentials", "projects", "portfolio", "availability"]
    visible_fields: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    # Optional self-declared fields
    preferred_opportunity_types: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    availability_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    availability_note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Opt-in to employer discoverability
    discoverable: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    # Scoped discoverability: NULL = all employers; list = specific employer_ids
    discoverable_to: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
```

A `SkillPassport` row is auto-created on first access (lazy init). The
default state is fully private and non-discoverable — users must
explicitly opt in.

**Never exposed externally**: raw AI evaluation scores, internal
discussion comments, billing data, cohort membership details,
password/tokens, protected/sensitive attributes.

### Passport share snapshots (§12)

```python
class PassportSnapshot(Base):
    """Immutable point-in-time snapshot for external verification."""
    __tablename__ = "passport_snapshots"

    id: Mapped[str] = ulid_pk()
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE")
    )
    # Share token for external URL: /verify/passport/{token}
    share_token: Mapped[str] = mapped_column(String(64), unique=True)
    # The frozen capability/credential/evidence summary
    payload: Mapped[dict] = mapped_column(JSONB)
    # SHA-256 of the canonical JSON payload — tamper detection
    checksum: Mapped[str] = mapped_column(String(64))
    # Which fields are included (user-selected subset)
    included_fields: Mapped[list] = mapped_column(JSONB)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # active | revoked
    status: Mapped[str] = mapped_column(String(20), default="active", server_default="'active'")

    __table_args__ = (
        Index("ix_snapshots_user", "user_id", "status"),
    )
```

**Verification flow**: `GET /verify/passport/{share_token}` returns the
frozen payload + checksum. The verifier can independently SHA-256 the
payload to confirm no tampering. No blockchain required.

Revoking a snapshot (`status → revoked`) makes the share URL return
`410 GONE` but does NOT rewrite the payload — if the snapshot was already
downloaded, the verifier retains their copy. This is by design (the
employer reviewed a specific version; future passport changes don't
retroactively alter what they saw).

---

## Decision 5 — Assessments and Credentials (Issue §13–§15)

### Assessment Blueprint

```python
class AssessmentBlueprint(Base):
    """Reusable standardized assessment definition."""
    __tablename__ = "assessment_blueprints"

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # knowledge | practical_task | portfolio_review | workflow_execution |
    # commercial_simulation | multi_stage_challenge
    assessment_type: Mapped[str] = mapped_column(String(30))
    # Capabilities this assessment evaluates, with thresholds
    # [{"capability_id": "01J...", "min_level": 3, "weight": 0.4}]
    capability_requirements: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    # Configuration: time_window_minutes, attempt_limit, required_deliverables,
    # rubric_id, workflow_restrictions, provider_restrictions,
    # human_review_required, reference_assets
    config: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    version: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    # draft | active | archived
    status: Mapped[str] = mapped_column(String(20), default="draft", server_default="'draft'")
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_blueprints_org", "org_id", "status"),
    )
```

### Assessment Run (§14)

```python
class AssessmentRun(Base):
    """A user's attempt at a specific assessment blueprint version."""
    __tablename__ = "assessment_runs"

    id: Mapped[str] = ulid_pk()
    blueprint_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("assessment_blueprints.id", ondelete="CASCADE")
    )
    blueprint_version: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE")
    )
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    attempt_number: Mapped[int] = mapped_column(Integer, default=1)
    # not_started | in_progress | submitted | under_review | passed | failed | expired
    status: Mapped[str] = mapped_column(String(20), default="not_started")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deadline_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Per-capability scores: [{"capability_id": "01J...", "score": 0.85, "passed": true}]
    results: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # Loose ref to project/submission created for practical assessments
    project_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_assessment_runs_user", "user_id", "blueprint_id"),
        Index("ix_assessment_runs_org", "org_id", "status"),
        # Enforce attempt limits at service level (not DB constraint —
        # config.attempt_limit may be NULL for unlimited)
    )
```

**Attempt limit enforcement**: Service-level check before creating a run:

```sql
SELECT COUNT(*) FROM assessment_runs
WHERE blueprint_id = :bid AND user_id = :uid AND attempt_number > 0
```

If count ≥ `blueprint.config.attempt_limit`, return 409
`ATTEMPT_LIMIT_REACHED`.

### Credential (§15)

```python
class Credential(Base):
    """Verified credential issued when a versioned rule set is satisfied."""
    __tablename__ = "credentials"

    id: Mapped[str] = ulid_pk()
    # "ai_product_visual_foundation" | "ai_product_visual_commercial" | etc.
    credential_type: Mapped[str] = mapped_column(String(80))
    version: Mapped[int] = mapped_column(Integer, default=1)
    # Platform or org that issued it
    issuer_org_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True
    )
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE")
    )
    # Capability requirements that were satisfied
    # [{"capability_id": "01J...", "required_level": 3, "achieved_level": 4}]
    capabilities: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    # Assessment/evidence IDs that satisfied the rule
    evidence_references: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    # active | expired | revoked | superseded
    status: Mapped[str] = mapped_column(String(20), default="active", server_default="'active'")
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revalidation_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_credentials_user", "user_id", "status"),
        Index("ix_credentials_type", "credential_type", "version"),
        # One active credential per (user, type) — superseding creates a new version
        Index(
            "uq_credential_active",
            "user_id", "credential_type",
            unique=True,
            postgresql_where=text("status = 'active'"),
        ),
    )
```

### Credential rule engine

```python
class CredentialRule(Base):
    """Versioned rule set for credential issuance — immutable once active."""
    __tablename__ = "credential_rules"

    id: Mapped[str] = ulid_pk()
    credential_type: Mapped[str] = mapped_column(String(80))
    version: Mapped[int] = mapped_column(Integer)
    # [{"capability_id": "01J...", "min_level": 3},
    #  {"assessment_blueprint_id": "01J...", "required": true}]
    requirements: Mapped[list] = mapped_column(JSONB)
    # Additional conditions: min_evidence_count, min_verification_level,
    # required_assessment_types, all_required (AND) vs any_required (OR)
    conditions: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    # draft | active | retired
    status: Mapped[str] = mapped_column(String(20), default="draft")
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("uq_credential_rule_version", "credential_type", "version", unique=True),
    )
```

Activating version N automatically retires version N-1. Rule evaluation
is a pure function: `evaluate_credential_rule(rule, user_profile) → bool`.
No side effects — credential issuance is a separate step that requires
the rule check AND human confirmation (for org-issued credentials) or
automatic issuance (for assessment-backed credentials with
`auto_issue=true` in the rule conditions).

---

## Decision 6 — Employer / Opportunity Model (Issue §16–§18)

### Employer entity

Employers are represented as Organizations with `org_type = 'employer'`.
This reuses existing auth/membership infrastructure while adding
employer-specific roles:

```python
# New enum values added to OrgRole (ADR-003):
# recruiter | hiring_manager | interviewer
# These roles only apply when the org has org_type='employer'.
# Permission checks: recruiter < hiring_manager < employer_admin < owner

class EmployerProfile(Base):
    """Employer-specific metadata on an Organization."""
    __tablename__ = "employer_profiles"

    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True
    )
    company_size: Mapped[str | None] = mapped_column(String(30), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    website_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # verified | pending | unverified
    verification_status: Mapped[str] = mapped_column(
        String(20), default="unverified", server_default="'unverified'"
    )
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
```

**Why reuse Organization, not a new top-level entity?** Organizations
already have tenant billing, membership, roles, invites, and IDOR-tested
isolation. Creating a parallel `Employer` entity would duplicate all
infrastructure. The `org_type` column (added to `organizations`) plus the
`employer_profiles` satellite table gives employers their identity while
reusing everything else.

New `OrgRole` values: `RECRUITER`, `HIRING_MANAGER`, `INTERVIEWER`. These
are added to the existing enum. The role hierarchy extends:

```python
EMPLOYER_ROLE_HIERARCHY = {
    OrgRole.OWNER: 0,
    OrgRole.ADMIN: 1,         # = employer_admin
    OrgRole.HIRING_MANAGER: 2,
    OrgRole.RECRUITER: 3,
    OrgRole.INTERVIEWER: 4,
    OrgRole.INSTRUCTOR: 2,    # unchanged for training orgs
    OrgRole.STUDENT: 3,       # unchanged for training orgs
}
```

### Opportunity (§17–§18)

```python
class Opportunity(Base):
    """A structured internship/job/project-role posting."""
    __tablename__ = "opportunities"

    id: Mapped[str] = ulid_pk()
    employer_org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # internship | full_time | part_time | contract | freelance |
    # project_role | apprenticeship | campus_project
    opportunity_type: Mapped[str] = mapped_column(String(30))
    # remote | onsite | hybrid
    location_mode: Mapped[str | None] = mapped_column(String(20), nullable=True)
    location_text: Mapped[str | None] = mapped_column(String(200), nullable=True)
    compensation_display: Mapped[str | None] = mapped_column(String(200), nullable=True)
    # Capability-based requirements (structured, powers matching):
    # [{"capability_id": "01J...", "min_level": 3, "required": true}]
    required_capabilities: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    # [{"capability_id": "01J...", "min_level": 2, "required": false}]
    preferred_capabilities: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    # self_reported | peer_verified | instructor_verified | assessment_verified | ...
    minimum_verification: Mapped[str | None] = mapped_column(String(30), nullable=True)
    portfolio_requirements: Mapped[str | None] = mapped_column(Text, nullable=True)
    application_deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    openings: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    # draft | open | closed | filled | cancelled
    status: Mapped[str] = mapped_column(String(20), default="draft", server_default="'draft'")
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_opportunities_employer", "employer_org_id", "status"),
        Index("ix_opportunities_type", "opportunity_type", "status"),
        Index("ix_opportunities_deadline", "application_deadline"),
    )
```

---

## Decision 7 — Talent ↔ Opportunity Matching (Issue §19–§22)

### Extend ADR-012 matching engine

A new `target_entity_type = "talent"` is added to the matching engine
with the following pipeline:

```
S1 eligibility     user.discoverable=true AND
                   (discoverable_to IS NULL OR employer_id IN discoverable_to) AND
                   passport.default_visibility != 'private'
S2 hard filters    required_capabilities: user level >= min_level
                   minimum_verification: at least one evidence at that level
S3 scoring         linear weighted sum (config v1 below)
S4 semantic        DEFERRED — socket for portfolio text similarity
S5 LLM explain     DEFERRED — socket for narrative match summary
```

**S1 is the consent gate**: candidates who have not set
`discoverable=true` are structurally invisible — they never enter the
candidate pool, period. This is not a filter; it's an eligibility
predicate that runs in SQL. The engine's SQL query for talent candidates:

```sql
SELECT u.id, u.display_name
FROM users u
JOIN skill_passports sp ON sp.user_id = u.id
WHERE sp.discoverable = true
  AND (sp.discoverable_to IS NULL
       OR :employer_org_id = ANY(sp.discoverable_to))
  AND sp.default_visibility != 'private'
  AND u.status = 'active'
```

Note: **only `id` and `display_name`** enter the feature space. No
demographic, geographic (unless voluntarily provided), or protected
attributes.

### Talent matching config v1

```
Signal                    Weight
capability_gap_score       0.40    # how well user meets required + preferred
evidence_confidence        0.20    # avg verification weight of relevant evidence
evidence_recency           0.15    # freshness of most recent evidence per required cap
portfolio_relevance        0.15    # count of approved projects in required capabilities
credential_match           0.10    # relevant active credentials
```

### Candidate-side opportunity matching (§20)

Users can call `GET /api/v1/talent/opportunities/matches` to see
opportunities ranked for them. The pipeline runs in reverse:

```
S1 eligibility     opportunity.status = 'open'
S2 hard filters    user meets all required_capabilities at min_level
S3 scoring         same signals, inverted perspective
```

Output:

```json
{
  "opportunity_id": "01J...",
  "match_score": 0.88,
  "tier": "great",
  "reasons": [
    {
      "code": "CAPABILITY_EXCEEDS",
      "label": "Product Visual L4 (required L3)",
      "evidence": "verified"
    },
    { "code": "CREDENTIAL_MATCH", "label": "AI Product Visual — Commercial Ready" }
  ],
  "gaps": [{ "code": "CAPABILITY_BELOW", "label": "Image-to-Video L1 (preferred L2)" }]
}
```

### Human decision authority (§22)

**Structural enforcement**: There is no `auto_hire`, `auto_reject`, or
`auto_offer` status transition in the `Application` state machine. Every
consequential transition (`→ offer`, `→ rejected`, `→ hired`) requires an
authenticated user with `hiring_manager+` role. The test suite asserts
that no service method performs these transitions without an explicit
`acted_by` user parameter.

---

## Decision 8 — Application / Placement Pipeline (Issue §23–§26)

### Application model

```python
class Application(Base):
    """Candidate's application to an opportunity."""
    __tablename__ = "applications"

    id: Mapped[str] = ulid_pk()
    opportunity_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("opportunities.id", ondelete="CASCADE")
    )
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE")
    )
    # Frozen snapshot of selected passport evidence at application time
    evidence_bundle: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    # Optional passport snapshot ID attached to this application
    passport_snapshot_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("passport_snapshots.id", ondelete="SET NULL"), nullable=True
    )
    # Match run that surfaced this opportunity (provenance)
    match_run_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    # draft | submitted | screening | interview | assessment | offer |
    # accepted | rejected | withdrawn | hired | completed
    status: Mapped[str] = mapped_column(String(20), default="draft", server_default="'draft'")
    # Resume/cover letter (optional, file upload)
    resume_asset_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    cover_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        # One application per (user, opportunity)
        Index("uq_application", "user_id", "opportunity_id", unique=True),
        Index("ix_applications_opportunity", "opportunity_id", "status"),
        Index("ix_applications_user", "user_id", "status"),
    )
```

### Application state machine

```
VALID_TRANSITIONS = {
    "draft":       ["submitted", "withdrawn"],
    "submitted":   ["screening", "rejected", "withdrawn"],
    "screening":   ["interview", "assessment", "rejected", "withdrawn"],
    "interview":   ["assessment", "offer", "rejected", "withdrawn"],
    "assessment":  ["interview", "offer", "rejected", "withdrawn"],
    "offer":       ["accepted", "rejected", "withdrawn"],
    "accepted":    ["hired", "withdrawn"],
    "rejected":    [],          # terminal
    "withdrawn":   [],          # terminal
    "hired":       ["completed"],
    "completed":   [],          # terminal
}
```

Every transition logged in `ApplicationEvent`:

```python
class ApplicationEvent(Base):
    """Audit trail for application status changes."""
    __tablename__ = "application_events"

    id: Mapped[str] = ulid_pk()
    application_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("applications.id", ondelete="CASCADE")
    )
    from_status: Mapped[str] = mapped_column(String(20))
    to_status: Mapped[str] = mapped_column(String(20))
    acted_by: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE")
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_app_events_application", "application_id", "created_at"),
    )
```

### Evidence bundle immutability (§24)

`evidence_bundle` is frozen at submission time. Future passport changes do
NOT update the bundle. The bundle stores:

```json
{
  "snapshot_at": "2026-09-13T08:00:00Z",
  "capabilities": [
    { "capability_id": "01J...", "name": "Product Visual Design", "level": 4, "score": 0.84 }
  ],
  "credentials": [
    { "credential_id": "01J...", "type": "ai_product_visual_commercial", "status": "active" }
  ],
  "selected_projects": ["01J...", "01J..."],
  "selected_evidence": ["01J...", "01J..."]
}
```

### Interview stages (§25)

```python
class InterviewStage(Base):
    """Structured interview/evaluation record."""
    __tablename__ = "interview_stages"

    id: Mapped[str] = ulid_pk()
    application_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("applications.id", ondelete="CASCADE")
    )
    stage_type: Mapped[str] = mapped_column(String(30))  # phone | technical | portfolio | panel | final
    interviewer_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Employer-private evaluation notes — NEVER exposed to other employers or the candidate
    evaluation_notes: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # pending | completed | cancelled | no_show
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_interview_stages_app", "application_id"),
    )
```

**Privacy**: `evaluation_notes` is employer-private. The API response
schema for candidate-facing endpoints structurally excludes this field
(the Pydantic response model does not declare it). Cross-employer
isolation: interview data is scoped by `application.opportunity.employer_org_id`;
queries always filter by the requesting user's org membership.

### Placement record (§26)

```python
class Placement(Base):
    """Outcome record when an application reaches hired status."""
    __tablename__ = "placements"

    id: Mapped[str] = ulid_pk()
    application_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("applications.id", ondelete="CASCADE"), unique=True
    )
    opportunity_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("opportunities.id", ondelete="CASCADE")
    )
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE")
    )
    employer_org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    role_title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Privacy-controlled: only visible to the user and employer admin
    compensation_band: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # platform_match | direct_apply | referral | cohort_exposure
    placement_source: Mapped[str | None] = mapped_column(String(30), nullable=True)
    # active | completed | terminated | cancelled
    status: Mapped[str] = mapped_column(String(20), default="active", server_default="'active'")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_placements_user", "user_id"),
        Index("ix_placements_employer", "employer_org_id", "status"),
    )
```

---

## Decision 9 — Internship / School Placement (Issue §27–§29)

### Cohort-to-opportunity exposure

```python
class CohortOpportunityExposure(Base):
    """School recommends/exposes opportunities to a cohort."""
    __tablename__ = "cohort_opportunity_exposures"

    id: Mapped[str] = ulid_pk()
    cohort_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("cohorts.id", ondelete="CASCADE")
    )
    opportunity_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("opportunities.id", ondelete="CASCADE")
    )
    exposed_by: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE")
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("uq_cohort_exposure", "cohort_id", "opportunity_id", unique=True),
    )
```

**Consent gate**: Exposing an opportunity to a cohort does NOT share
student data. Students see the opportunity in their dashboard and must
individually opt in (set `discoverable=true` + apply) before the employer
can see any of their data.

### Internship supervision (§28)

```python
class InternshipSupervision(Base):
    """School-side tracking of an internship placement."""
    __tablename__ = "internship_supervisions"

    id: Mapped[str] = ulid_pk()
    placement_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("placements.id", ondelete="CASCADE"), unique=True
    )
    # School org that placed the student
    school_org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    supervisor_user_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    employer_mentor_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # Structured milestones: [{"title": "...", "due_date": "...", "status": "pending|done"}]
    milestones: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    # Manual notes (weekly check-ins, attendance, engagement)
    notes: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    # pending | active | completed | terminated
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_supervisions_school", "school_org_id", "status"),
    )
```

### Employer verification → evidence (§29)

```python
class EmployerVerification(Base):
    """Structured capability verification from an employer after a placement."""
    __tablename__ = "employer_verifications"

    id: Mapped[str] = ulid_pk()
    placement_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("placements.id", ondelete="CASCADE")
    )
    employer_org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    verified_by: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE")
    )
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE")
    )
    # Per-capability ratings the employer observed:
    # [{"capability_id": "01J...", "level_observed": 4, "score": 0.85, "comment": "..."}]
    capability_ratings: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    overall_rating: Mapped[float | None] = mapped_column(Numeric(3, 2), nullable=True)
    overall_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_employer_verifications_placement", "placement_id"),
        Index("ix_employer_verifications_user", "user_id"),
    )
```

On creation, the service automatically generates `capability_evidence`
rows with `source_type='employment_verification'`,
`verification_level='employer_verified'` for each rated capability. The
employer's rating `score` is normalized to [0,1] and stored as
`score_normalized`. This is the highest-trust evidence tier (weight 1.0).

**Scope enforcement**: The `capability_ratings` are validated against the
opportunity's `required_capabilities ∪ preferred_capabilities`. An
employer cannot rate a capability not listed in the opportunity — this
prevents scope creep where an employer rates capabilities they never
observed.

---

## Decision 10 — Outcome Tracking and Alumni (Issue §30–§31)

### Outcome events

```python
class OutcomeEvent(Base):
    """Longitudinal career milestone — user-controlled visibility."""
    __tablename__ = "outcome_events"

    id: Mapped[str] = ulid_pk()
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE")
    )
    # internship_started | internship_completed | job_offer_received |
    # job_started | contract_project_completed | promotion | role_change |
    # credential_renewed | capability_reverified
    event_type: Mapped[str] = mapped_column(String(40))
    # Loose reference to the source entity (placement, credential, etc.)
    source_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    source_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    # User-controlled visibility: private | passport_visible | public
    visibility: Mapped[str] = mapped_column(String(20), default="private", server_default="'private'")
    metadata: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_outcome_events_user", "user_id", "event_type"),
    )
```

Some events are auto-generated (e.g., placement status → `hired` creates
`job_started`), others are user-confirmed (e.g., `promotion` requires the
user to submit it). Auto-generated events default to `private` — the user
must explicitly change visibility.

### Alumni continuity (§31)

The `SkillPassport` and `capability_evidence` are user-scoped, NOT
org-scoped. When a user graduates from a cohort or leaves an
organization:

1. Their `capability_evidence` rows persist (the `org_id` on evidence is
   informational — it records where the evidence was earned, not who owns
   it).
2. Their `SkillPassport` is unchanged.
3. Their `credentials` remain active (credentials are user-owned).
4. Org-specific access to source records (e.g., project submissions,
   rubric reviews) follows existing org membership rules — if the user
   loses org access, the evidence row persists but the provenance chain
   may show `redacted` links.

A user maintains a single longitudinal identity across multiple schools,
cohorts, employers, and commercial projects. There is no "alumni" status
in the user model — the passport IS the continuous identity.

---

## Decision 11 — Workforce Intelligence (Issue §32–§34)

### Demand signal aggregation

The system computes demand by counting capability references across:

- Open `opportunities.required_capabilities` + `preferred_capabilities`
- Active `client_briefs.structured_requirements.required_capabilities`
- Recent `match_runs` with `target_entity_type='talent'`

**Privacy threshold**: Aggregates are only returned when the underlying
count ≥ `settings.workforce_min_cohort_size` (default: 10). Below this
threshold, the capability row is suppressed from the output (not
rounded to 10, which would leak the exact value for small N).

### Supply intelligence

Verified supply = count of users with `capability_evidence.status='active'`
at each level, filtered to `discoverable=true` users only (or to the
requesting org's own members for school dashboards).

### Gap analysis output

```json
{
  "capability_id": "01J...",
  "capability": "Image-to-Video Production",
  "demand_count": 280,
  "supply_by_level": { "L1": 40, "L2": 30, "L3": 15, "L4": 8, "L5": 2 },
  "qualified_supply": 95,
  "gap": 185,
  "gap_severity": "high",
  "content_coverage": {
    "skill_packs": 2,
    "assessments": 0,
    "project_templates": 1,
    "workflows": 3
  }
}
```

`gap_severity` = `high` when gap/demand > 0.5, `medium` when > 0.25,
`low` otherwise. This is a presentation aid, not a decision rule.

### Materialized aggregate views

```sql
CREATE MATERIALIZED VIEW mv_workforce_demand AS
SELECT
  c.id AS capability_id,
  c.canonical_name,
  COUNT(DISTINCT o.id) FILTER (WHERE o.status = 'open') AS open_opportunities,
  COUNT(DISTINCT cb.id) FILTER (WHERE cb.status = 'active') AS active_briefs,
  COUNT(DISTINCT o.id) + COUNT(DISTINCT cb.id) AS total_demand
FROM capabilities c
LEFT JOIN LATERAL (
  SELECT o.id, o.status
  FROM opportunities o, jsonb_array_elements(o.required_capabilities) AS rc
  WHERE rc->>'capability_id' = c.id
) o ON true
LEFT JOIN LATERAL (
  SELECT cb.id, cb.status
  FROM client_briefs cb
  WHERE cb.structured_requirements->'required_capabilities' @> jsonb_build_array(jsonb_build_object('capability_id', c.id))
) cb ON true
WHERE c.status = 'active'
GROUP BY c.id, c.canonical_name;
```

Refreshed hourly by arq worker. Dashboard queries read from the
materialized view, never from raw opportunity/brief tables.

---

## Decision 12 — Curriculum Intelligence (Issue §35–§37)

### Coverage matrix (§35)

For each capability, compute coverage from `capability_mappings`:

```json
{
  "capability_id": "01J...",
  "capability": "Character Consistency",
  "demand_index": 92,
  "verified_supply": 31,
  "content_coverage": [
    { "type": "skill_pack", "id": "01J...", "title": "Character Basics", "weight": 0.3 },
    { "type": "workflow_pack", "id": "01J...", "title": "Short Drama Setup", "weight": 0.2 }
  ],
  "coverage_gaps": [
    "No commercial-ready assessment (assessment_blueprint count = 0)",
    "No advanced project template (project_template count = 0)"
  ]
}
```

### Outcome-based analytics (§36)

Join learning content completion → downstream outcomes:

```
capability_evidence (source_type=skill_completion, source_id=skill_pack X)
  → assessment_runs (passed, for capabilities mapped to skill_pack X)
  → placements (user_id, employer_org_id, status=completed)
  → employer_verifications (capability scores for same user)
```

These are presented as **observed associations** with explicit caveats:
"Learners who completed Pack X had a 73% assessment pass rate (N=42)."
No causal claims.

### Content improvement recommendations (§37)

The system generates structured recommendations but **never auto-publishes
or auto-edits content**:

```json
{
  "recommendation_type": "add_assessment",
  "capability_id": "01J...",
  "capability": "Character Consistency",
  "reason": "High demand (92 idx), no standardized assessment exists",
  "suggested_action": "Create practical assessment blueprint for Character Consistency",
  "confidence": "high",
  "requires_confirmation": true
}
```

All recommendations surface in the school dashboard with an explicit
"Accept / Dismiss" action. Dismissing logs the decision (audit).

---

## Decision 13 — Talent CRM (Issue §38–§39)

### Talent pools

```python
class TalentPool(Base):
    """Consent-based talent pool for grouping candidates."""
    __tablename__ = "talent_pools"

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # manual | rule_suggested | candidate_opt_in
    membership_mode: Mapped[str] = mapped_column(String(20), default="manual")
    # For rule_suggested: {"min_level": 3, "capabilities": ["01J..."], ...}
    rule_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # Only visible to members of the owning org
    # internal | shared (visible to member candidates)
    visibility: Mapped[str] = mapped_column(String(20), default="internal")
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_talent_pools_org", "org_id"),
    )


class TalentPoolMembership(Base):
    __tablename__ = "talent_pool_memberships"

    id: Mapped[str] = ulid_pk()
    pool_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("talent_pools.id", ondelete="CASCADE")
    )
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE")
    )
    # manual_added | rule_suggested | opted_in
    source: Mapped[str] = mapped_column(String(20))
    # For rule_suggested: pending_consent | accepted | declined
    # For manual/opted_in: accepted (always)
    consent_status: Mapped[str] = mapped_column(String(20), default="accepted")
    added_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("uq_pool_member", "pool_id", "user_id", unique=True),
        Index("ix_pool_memberships_user", "user_id"),
    )
```

**Rule-suggested pools**: The rule engine matches users against
`rule_config` criteria but sets `consent_status='pending_consent'`. The
user sees a notification and must accept before their data is visible in
the pool. This prevents silent enrollment into externally-visible pools.

### Outreach / invitations (§39)

```python
class TalentOutreach(Base):
    """Opportunity invitation or talent-pool invitation."""
    __tablename__ = "talent_outreach"

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE")
    )
    # opportunity_invitation | pool_invitation
    outreach_type: Mapped[str] = mapped_column(String(30))
    # Reference to opportunity or pool
    target_type: Mapped[str] = mapped_column(String(20))
    target_id: Mapped[str] = mapped_column(String(26))
    # sent | viewed | accepted | declined | expired
    status: Mapped[str] = mapped_column(String(20), default="sent")
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_outreach_user", "user_id", "status"),
        Index("ix_outreach_org", "org_id"),
        # Anti-spam: max 3 outreach per (org, user) per 30 days, enforced at service level
    )
```

**Anti-spam**: Service-level rate limit: max 3 outreach messages from the
same org to the same user within 30 days. Exceeding → 429
`OUTREACH_RATE_LIMITED`.

---

## Decision 14 — API Surface

All talent APIs live under `/api/v1/talent/`:

```
# Capability Ontology
GET     /talent/capabilities                    # list (paginated, filterable)
POST    /talent/capabilities                    # create (platform admin)
GET     /talent/capabilities/{id}               # detail with relationships
PATCH   /talent/capabilities/{id}               # update
POST    /talent/capabilities/{id}/edges         # add relationship
DELETE  /talent/capabilities/{id}/edges/{eid}   # remove relationship
GET     /talent/capabilities/{id}/graph         # bounded traversal (depth param)
POST    /talent/capability-mappings             # map content to capability
GET     /talent/capability-mappings             # list mappings

# Evidence Ledger
GET     /talent/evidence                        # own evidence (user) or admin query
POST    /talent/evidence                        # record evidence (service/admin)
GET     /talent/evidence/{id}                   # detail with provenance chain
POST    /talent/evidence/{id}/void              # void evidence

# Capability Profile
GET     /talent/users/{uid}/profile             # derived capability profile
GET     /talent/users/{uid}/capabilities        # paginated capability list with scores

# Skill Passport
GET     /talent/passport                        # own passport
PATCH   /talent/passport                        # update privacy/visibility settings
POST    /talent/passport/snapshots              # generate share snapshot
GET     /talent/passport/snapshots              # list own snapshots
DELETE  /talent/passport/snapshots/{id}         # revoke snapshot
GET     /verify/passport/{token}                # public verification (no auth)

# Assessments
POST    /talent/assessments                     # create blueprint (instructor+)
GET     /talent/assessments                     # list
GET     /talent/assessments/{id}                # detail
POST    /talent/assessments/{id}/runs           # start attempt
PATCH   /talent/assessments/{id}/runs/{rid}     # submit / update
POST    /talent/assessments/{id}/runs/{rid}/review  # instructor review

# Credentials
GET     /talent/credentials                     # own credentials
GET     /talent/credentials/{id}                # detail
POST    /talent/credential-rules                # define rule (admin)
POST    /talent/credentials/evaluate            # check if user qualifies
POST    /talent/credentials/issue               # issue credential

# Employers & Opportunities
POST    /talent/employers                       # register employer profile
GET     /talent/employers/{org_id}              # employer profile
POST    /talent/opportunities                   # create (employer)
GET     /talent/opportunities                   # list open
GET     /talent/opportunities/{id}              # detail
PATCH   /talent/opportunities/{id}              # update
GET     /talent/opportunities/matches           # candidate-side matching

# Talent Matching (employer side)
POST    /talent/opportunities/{id}/match        # generate candidate shortlist
GET     /talent/match-runs/{id}                 # view match results

# Applications
POST    /talent/opportunities/{id}/apply        # submit application
GET     /talent/applications                    # own applications (candidate)
GET     /talent/applications/{id}               # detail
PATCH   /talent/applications/{id}/status        # transition (employer)
POST    /talent/applications/{id}/interviews    # add interview stage
PATCH   /talent/applications/{id}/interviews/{iid}  # update interview

# Placements
POST    /talent/placements                      # create on hire
GET     /talent/placements                      # list (user or employer)
PATCH   /talent/placements/{id}                 # update status/dates
POST    /talent/placements/{id}/verification    # employer verification

# Internship Supervision
POST    /talent/supervisions                    # create (school)
GET     /talent/supervisions                    # list (school)
PATCH   /talent/supervisions/{id}               # update milestones/notes

# Cohort Exposure
POST    /talent/cohorts/{cid}/expose            # expose opportunity to cohort
GET     /talent/cohorts/{cid}/opportunities     # list exposed opportunities

# Outcome Events
GET     /talent/outcomes                        # own outcome events
POST    /talent/outcomes                        # record event

# Talent Pools
POST    /talent/pools                           # create
GET     /talent/pools                           # list (org)
POST    /talent/pools/{id}/members              # add/invite member
PATCH   /talent/pools/{id}/members/{mid}        # respond to invitation
GET     /talent/pools/{id}/members              # list members

# Outreach
POST    /talent/outreach                        # send invitation
GET     /talent/outreach                        # list sent (org) or received (user)
PATCH   /talent/outreach/{id}                   # respond

# Workforce Intelligence
GET     /talent/intelligence/demand             # demand by capability
GET     /talent/intelligence/supply             # supply by capability
GET     /talent/intelligence/gaps               # demand-supply gaps
GET     /talent/intelligence/coverage           # curriculum coverage matrix
GET     /talent/intelligence/outcomes           # outcome analytics

# Dashboards (aggregated)
GET     /talent/dashboards/school               # school dashboard data
GET     /talent/dashboards/employer             # employer dashboard data
GET     /talent/dashboards/platform             # platform workforce dashboard
```

### Webhook events (reuse existing infrastructure)

New event topics added to the webhook system:

```
credential.issued
credential.revoked
application.submitted
application.stage_changed
offer.created
placement.started
placement.completed
capability.verified
employer_verification.submitted
outreach.sent
outreach.responded
talent_pool.member_added
```

---

## Decision 15 — Privacy, Fairness and Safety (Issue Part P)

### Structural privacy guarantees

1. **Discoverability is opt-in**: `skill_passports.discoverable = false`
   (default). S1 eligibility in talent matching queries
   `WHERE discoverable = true` — non-discoverable users are structurally
   absent, not filtered.

2. **Field-level sharing**: `visible_fields` whitelist on `SkillPassport`.
   The response serializer checks each field against this list before
   rendering. Unknown fields default to hidden.

3. **No protected attributes in matching**: The talent matching candidate
   query selects ONLY `users.id, users.display_name`. No age, gender,
   race, religion, health, location (unless voluntarily provided in
   passport), or any inferred sensitive trait enters the feature space.
   This is structural (column selection in SQL), not policy-based
   filtering.

4. **No automatic consequential decisions**: The `Application` state
   machine has no transitions without `acted_by`. The service method
   signatures enforce this:

   ```python
   async def transition_application(
       self, db, application_id, to_status, acted_by: str, note: str | None
   ) -> Application:
   ```

   `acted_by` is NOT nullable — the caller must provide a real user ID.

5. **Interview privacy**: `evaluation_notes` excluded from candidate
   response schemas. Cross-employer queries filtered by org membership.

6. **Workforce analytics privacy**: Aggregates suppressed below
   `min_cohort_size` (configurable, default 10).

7. **Evidence authorization**: Provenance chain walks check access per
   link; inaccessible links render as `redacted`.

8. **Snapshot immutability**: Share snapshots are frozen. Revoking makes
   the URL return 410 but doesn't rewrite the payload.

### Cross-tenant/cross-employer IDOR tests

Every talent API endpoint must have at least one test asserting:

- User A (employer org 1) cannot read user B's application to employer org 2.
- User A cannot transition an application belonging to employer org 2.
- Employer 1 cannot read interview notes from employer 2.
- School 1 cannot read supervision records from school 2.
- Non-discoverable user does not appear in any talent matching result.
- User cannot rate a capability not on the opportunity.

---

## Decision 16 — Migration Strategy

### Phase 1 — Foundation (capabilities, evidence, scoring, passport)

1. Migration `talent01`: `capabilities`, `capability_edges`,
   `capability_mappings` tables. Seed initial capabilities from existing
   `capability_tags` where applicable.
2. Migration `talent02`: `capability_evidence` table. Migrate existing
   `creator_capability_evidence` rows.
3. Migration `talent03`: `skill_passports`, `passport_snapshots`.
4. Migration `talent04`: `assessment_blueprints`, `assessment_runs`,
   `credential_rules`, `credentials`.

### Phase 2 — Employment marketplace

5. Migration `talent05`: `employer_profiles`, `opportunities`.
   Add `org_type` column to `organizations`, `RECRUITER` /
   `HIRING_MANAGER` / `INTERVIEWER` to `OrgRole` enum.
6. Migration `talent06`: `applications`, `application_events`,
   `interview_stages`, `placements`.

### Phase 3 — Internship, outcomes, intelligence

7. Migration `talent07`: `cohort_opportunity_exposures`,
   `internship_supervisions`, `employer_verifications`.
8. Migration `talent08`: `outcome_events`.
9. Migration `talent09`: `talent_pools`, `talent_pool_memberships`,
   `talent_outreach`.
10. Migration `talent10`: Materialized views for workforce intelligence.

### OrgRole enum extension

Adding values to a Postgres enum requires:

```sql
ALTER TYPE org_role ADD VALUE IF NOT EXISTS 'recruiter';
ALTER TYPE org_role ADD VALUE IF NOT EXISTS 'hiring_manager';
ALTER TYPE org_role ADD VALUE IF NOT EXISTS 'interviewer';
```

These are non-reversible in Postgres (enum values cannot be removed).
The migration is marked as non-downgradeable.

---

## Decision 17 — Testing Plan

### Unit/integration test files (in `tests/talent/`)

```
test_capabilities.py          — ontology CRUD, graph validation, cycle detection
test_capability_edges.py      — edge types, cycle rejection, bounded traversal
test_capability_mappings.py   — content mapping, weight validation
test_evidence.py              — append-only, void/supersede, idempotency, provenance
test_evidence_verification.py — verification levels, weight hierarchy
test_scoring.py               — algorithm v1, decay, levels, Bayesian shrinkage
test_passport.py              — private-by-default, field visibility, discoverable
test_passport_snapshots.py    — immutability, checksum, revocation, expiry
test_assessments.py           — blueprint lifecycle, attempt limits, scoring
test_credentials.py           — rule evaluation, issuance, expiration, revocation
test_employers.py             — employer profile, role permissions
test_opportunities.py         — CRUD, capability requirements, status lifecycle
test_talent_matching.py       — consent gate, hard constraints, scoring, explanation
test_applications.py          — state machine, transition auth, evidence bundle
test_interviews.py            — privacy isolation, cross-employer IDOR
test_placements.py            — lifecycle, placement source tracking
test_employer_verification.py — capability scope, evidence generation
test_internship.py            — cohort exposure, consent, supervision, milestone
test_outcomes.py              — event types, visibility, auto-generation
test_talent_pools.py          — membership modes, consent, rule-suggested
test_outreach.py              — rate limiting, status lifecycle
test_workforce_intelligence.py — aggregation, privacy thresholds, gap calc
test_curriculum_intel.py      — coverage matrix, outcome joins
test_talent_adversarial.py    — cross-tenant IDOR, protected-attribute exclusion,
                                no-auto-hire assertion, non-discoverable invisibility
```

### Browser E2E

`tests/browser_e2e_talent.mjs` — full lifecycle:

```
1.  Learner completes training (skill pack → exercise)
2.  Learner completes approved commercial project
3.  → capability evidence auto-generated
4.  Skill Passport shows verified capabilities
5.  Learner takes standardized practical assessment → passes
6.  → credential issued
7.  Employer registers, publishes internship requiring that capability
8.  Learner opts into discoverability
9.  Explainable match generated (candidate sees opportunity)
10. Learner applies with selected passport snapshot
11. Employer moves application: screening → interview → offer
12. Learner accepts offer
13. Placement created, internship starts
14. Employer completes placement evaluation (capability ratings)
15. → employer_verified evidence created
16. School outcome dashboard shows placement
17. Workforce gap / curriculum coverage dashboard updates
```

### Key test invariants (assert in `test_talent_adversarial.py`)

1. Non-discoverable user NEVER appears in any `POST .../match` result.
2. No `Application` transition to `offer/rejected/hired` without `acted_by`.
3. `CapabilityEvidence` UPDATE on any column except `status` → raises.
4. Protected attributes (race, religion, gender, age, health, sexual
   orientation, political beliefs) are structurally absent from talent
   matching SQL queries (verified by query inspection or mock).
5. `PassportSnapshot.payload` is byte-identical on re-read after creation.
6. Workforce aggregate with < `min_cohort_size` returns no row for that
   capability (not a rounded/clamped value).
7. Cross-employer interview note isolation: employer A cannot read
   employer B's `evaluation_notes`.
8. Employer cannot rate a capability not in the opportunity's
   `required_capabilities ∪ preferred_capabilities`.

---

## Known Limitations (v1, deliberate)

- Capability ontology is platform-managed only (no org-scoped custom
  capabilities in v1; org extensions via `CapabilityTag` x-prefix remain
  for workflow I/O only).
- S4 (semantic) and S5 (LLM rerank/explain) for talent matching are
  deferred sockets — config reserves keys but implementation is Phase 2.
- Materialized views for workforce intelligence are refreshed hourly, not
  real-time (acceptable for dashboard use cases).
- Credential rule engine evaluates AND/OR of requirements but not
  arbitrary boolean expressions (sufficient for all described use cases).
- Compensation data (`compensation_display`, `compensation_band`) is
  free-text, not structured — no compensation analytics in v1.
- No automated dunning or suspension for employer accounts (handled by
  existing SaaS control plane if employers are tenants).
- Assessment practical runs create regular `Project` records — no
  separate sandboxed execution environment.
- Alumni "multi-school" identity relies on email uniqueness — no federated
  identity protocol in v1.
- Outreach anti-spam is service-level, not Redis-backed rate limiting
  (sufficient at expected v1 volumes).

---

## Verification

- Per-domain unit/integration test suites (≥30 files, see Decision 17).
- `test_talent_adversarial.py`: all 8 invariants from Decision 15/17.
- `tests/e2e_talent_lifecycle.py`: live-API chain covering the full
  learn → prove → credential → match → apply → hire → verify → dashboard
  pipeline, zero 500s.
- `tests/browser_e2e_talent.mjs`: Playwright pass over the talent
  frontend, zero console errors, zero API 500s.
- Ruff + type-check pass on all new code.
- All existing tests continue to pass (no regressions).

---

## Implementation Record (PR #33)

**Implemented**: September 2026
**Branch**: `feature/talent-graph-passport-marketplace`
**Commits**: 90+

### Deliverables

| Category | Count |
|----------|-------|
| Backend models | 27 files, 48 classes |
| Backend services | 64 files |
| API routers | 37 files, 270+ endpoints |
| Frontend pages | 29 talent pages |
| Migrations | 15 (talent01–talent15) |
| pytest | 2,748 passing |
| Playwright | 497 passing (501 total, 4 skipped) |
| 1-hour marathon | 49,404 HTTP requests, 0 failures |

### Architecture

```
app/talent/
├── models/     27 SQLAlchemy models (ULID PKs, JSONB fields)
├── schemas/    Pydantic v2 schemas (from_attributes=True)
├── services/   64 service modules (pure business logic)
├── api/        37 FastAPI routers (270+ endpoints)
└── facade.py   Service locator for cross-module access
```

### Key Technical Decisions Validated

1. **4-dimensional scoring** (depth/breadth/recency/velocity) — SCORING_VERSION "2.0.0"
2. **Ed25519 credential signing** — W3C Verifiable Credentials + Open Badges 3.0
3. **EEOC four-fifths rule** — adverse impact ratio in fairness metrics
4. **Cursor-based pagination** — ULID-ordered, no offset skip
5. **Redis caching** — scoring profiles (5min TTL), graceful degradation
6. **N+1 fix** — batch loading for matching (3 queries vs 3×N)
7. **In-memory rate limiter** — sliding window, no auth dependency on public routes

### Production Enhancements (post-core)

- **Recharts** — interactive RadarChart, BarChart, LineChart with tooltips
- **Full CRUD** — career goals edit/delete, portfolio reorder, opportunity bookmark/apply
- **Redis cache module** — `app/talent/services/cache.py`
- **Performance indexes** — 3 composite/single indexes on hot query paths
- **API documentation** — summary/description on 78 route decorators
- **Outreach API** — send/list/respond with access control
- **Alumni mode** — passport field for graduated learners

### CI Integration

- `test-talent` job: runs 2,748 talent unit tests (no DB, ~6 min)
- `test-playwright` job: runs 200 E2E browser tests (talent + sweep)
- `test-backend` job: runs full suite with DB, Redis, MinIO
