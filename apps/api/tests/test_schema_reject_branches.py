"""R211-R216: schema-validator reject-branch coverage (branch-gap sweep).

Every Pydantic field_validator's REJECT arc is a robustness/security
sentinel: weakening one lets oversized text, out-of-range numbers, wrong
enum values, or malformed structure reach the DB write (→ 500 or corrupt
row). Full-suite branch analysis flagged ~240 of these across the schema
layer as never exercised on their reject side. Each case below drives one
guard to its ValueError and asserts the request is rejected.
"""

import pytest
from pydantic import ValidationError


def _rejects(model, base: dict, field: str, bad):
    """Assert model(**{**base, field: bad}) raises ValidationError."""
    with pytest.raises(ValidationError):
        model(**{**base, field: bad})


# ── project.py ───────────────────────────────────────────────

_PROJ = dict(
    title="Valid Title", description="d", instructions="i",
    rubric=[{"criterion": "Quality", "max_score": 100}],
)


def test_create_project_rejects():
    from app.schemas.project import CreateProjectRequest as M

    # positive control
    assert M(**_PROJ).max_score == 100
    _rejects(M, _PROJ, "project_type", "not_a_type")
    _rejects(M, _PROJ, "difficulty", "wizard")
    _rejects(M, _PROJ, "max_score", 0)
    _rejects(M, _PROJ, "max_score", 10001)
    _rejects(M, _PROJ, "title", "x")                    # <2 chars
    _rejects(M, _PROJ, "title", "y" * 201)              # >200
    _rejects(M, _PROJ, "rubric", [])                    # empty
    _rejects(M, _PROJ, "rubric", [{}] * 21)             # >20
    _rejects(M, _PROJ, "rubric", ["not-a-dict"])
    _rejects(M, _PROJ, "rubric", [{"max_score": 5}])    # missing criterion
    _rejects(M, _PROJ, "rubric", [{"criterion": "c"}])  # missing max_score
    _rejects(M, _PROJ, "rubric", [{"criterion": "c", "max_score": -1}])
    _rejects(M, _PROJ, "rubric", [{"criterion": "x" * 201, "max_score": 1}])
    _rejects(M, _PROJ, "slug", "s" * 201)
    _rejects(M, _PROJ, "late_penalty_pct", 101)
    _rejects(M, _PROJ, "late_penalty_pct", -1)
    _rejects(M, _PROJ, "max_submissions", 1001)
    _rejects(M, _PROJ, "max_submissions", -1)
    _rejects(M, _PROJ, "description", "d" * 10001)
    _rejects(M, _PROJ, "instructions", "i" * 50001)


def test_create_project_deadline_ordering():
    from datetime import UTC, datetime, timedelta

    from app.schemas.project import CreateProjectRequest as M

    dl = datetime(2026, 6, 1, tzinfo=UTC)
    with pytest.raises(ValidationError):
        M(**_PROJ, deadline=dl, late_deadline=dl - timedelta(days=1))
    # valid ordering passes
    ok = M(**_PROJ, deadline=dl, late_deadline=dl + timedelta(days=1))
    assert ok.late_deadline > ok.deadline


# ── skill.py ─────────────────────────────────────────────────

_SKILL = dict(category_id="c", name="Valid Skill", description="d")


def test_create_skill_rejects():
    from app.schemas.skill import CreateSkillRequest as M

    assert M(**_SKILL).difficulty == "beginner"
    _rejects(M, _SKILL, "difficulty", "wizard")
    _rejects(M, _SKILL, "name", "x")
    _rejects(M, _SKILL, "name", "y" * 201)
    _rejects(M, _SKILL, "description", "d" * 10001)
    _rejects(M, _SKILL, "learning_content", "l" * 100001)
    _rejects(M, _SKILL, "slug", "s" * 201)
    _rejects(M, _SKILL, "estimated_minutes", -1)
    _rejects(M, _SKILL, "estimated_minutes", 10000)
    # NUL control char in a screened text field
    _rejects(M, _SKILL, "name", "bad\x00name")


# ── skill_pack.py ────────────────────────────────────────────

_PACK = dict(name="Valid Pack")


def test_create_skill_pack_rejects():
    from app.schemas.skill_pack import CreateSkillPackRequest as M

    assert M(**_PACK).visibility == "private"
    _rejects(M, _PACK, "name", "x")
    _rejects(M, _PACK, "name", "y" * 201)
    _rejects(M, _PACK, "summary", "s" * 501)
    _rejects(M, _PACK, "visibility", "cosmic")
    _rejects(M, _PACK, "difficulty", "wizard")
    _rejects(M, _PACK, "description", "d" * 10001)
    _rejects(M, _PACK, "scenario_tags", ["ok", "x" * 101])
    _rejects(M, _PACK, "scenario_tags", ["t"] * 51)
    _rejects(M, _PACK, "learning_outcomes", ["o"] * 21)
    _rejects(M, _PACK, "learning_outcomes", ["x" * 501])
    _rejects(M, _PACK, "estimated_minutes", -1)
    _rejects(M, _PACK, "estimated_minutes", 10000)


# ── workflow_pack.py ─────────────────────────────────────────

_WF = dict(name="Valid WF Pack")


def test_create_workflow_pack_rejects():
    from app.schemas.workflow_pack import CreateWorkflowPackRequest as M

    assert M(**_WF).workflow_type == "production"
    _rejects(M, _WF, "name", "")
    _rejects(M, _WF, "name", "y" * 201)
    _rejects(M, _WF, "summary", "s" * 501)
    _rejects(M, _WF, "description", "d" * 20001)
    _rejects(M, _WF, "workflow_type", "chaotic")
    _rejects(M, _WF, "difficulty", "wizard")
    _rejects(M, _WF, "language", "not-a-language-code")
    _rejects(M, _WF, "tool_tags", ["t"] * 21)
    _rejects(M, _WF, "tool_tags", ["  "])              # empty-after-strip
    _rejects(M, _WF, "tool_tags", ["x" * 51])
    _rejects(M, _WF, "provenance", {"k": "v" * 20001})


# ── client_brief.py ──────────────────────────────────────────

_CB = dict(title="Valid Brief", client_name="Acme", project_type="ai_visual", objective="a valid objective")


def test_create_client_brief_rejects():
    from app.schemas.client_brief import CreateClientBriefRequest as M

    assert M(**_CB).client_name == "Acme"
    _rejects(M, _CB, "title", "x")               # <2
    _rejects(M, _CB, "title", "y" * 301)         # >300
    _rejects(M, _CB, "client_name", "")          # <1
    _rejects(M, _CB, "client_name", "y" * 201)   # >200
    _rejects(M, _CB, "client_industry", "z" * 101)


# ── provider.py (offering) ───────────────────────────────────

_OFF = dict(connection_id="c", capability_key="text_generation", model_name="m")


def test_create_offering_rejects():
    from app.schemas.provider import CreateOfferingRequest as M

    assert M(**_OFF).quality_tier == "standard"
    _rejects(M, _OFF, "capability_key", "")
    _rejects(M, _OFF, "capability_key", "k" * 65)
    _rejects(M, _OFF, "model_name", "")
    _rejects(M, _OFF, "model_name", "m" * 201)
    _rejects(M, _OFF, "quality_tier", "legendary")
    _rejects(M, _OFF, "features", ["f"] * 21)
    _rejects(M, _OFF, "features", ["x" * 65])
    _rejects(M, _OFF, "cost_per_call_usd", float("nan"))
    _rejects(M, _OFF, "cost_per_call_usd", 10000.0)   # rounds to >= 10000
    _rejects(M, _OFF, "cost_per_call_usd", -1.0)
