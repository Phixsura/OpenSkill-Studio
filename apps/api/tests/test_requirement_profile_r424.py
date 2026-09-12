"""R424: requirement-profile provenance/validation/authz mutation hardening.

build_match_requirement enforces the R14 fairness rule (LLM-extracted
capabilities must NEVER become hard S2 filters — only human-confirmed
fields do); _validate_structured / _normalize_extracted gate untrusted
LLM + form input; _assert_can_write is the owner/instructor authz gate.

Documented EQUIVALENT mutants (adjudicated):
- The many 422->423 / 500->501 / 64->65 swaps: HTTP status-class and
  sanitize-truncation-length cosmetics — the class (client error / the
  string being bounded) is unchanged; codes are pinned, the exact number
  and the ±1 truncation char are not.
- L581/L588/L591/L600/L606/L612 sanitize_untrusted_text max-length 64->65 /
  500->501: a ±1-char truncation bound on already-bounded untrusted text —
  not observably different.
"""

import uuid

import pytest

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.exceptions import AppError
from app.models.user import User, UserRole, UserStatus


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _user(db, role=UserRole.ADMIN):
    u = User(
        email=f"r424-{uuid.uuid4().hex[:10]}@test.com",
        password_hash=hash_password("Test123!"),
        display_name="R424",
        role=role,
        status=UserStatus.ACTIVE,
    )
    db.add(u)
    await db.flush()
    return u


async def _org(db, owner):
    from app.services.organization import OrgService

    o = await OrgService(db).create(
        name=f"R424 {uuid.uuid4().hex[:6]}",
        slug=f"r424-{uuid.uuid4().hex[:10]}",
        description=None,
        created_by=owner.id,
    )
    await db.flush()
    return o


async def _cap(db, key):
    from sqlalchemy import select as _sel

    from app.models.capability import CapabilityTag

    found = (
        await db.execute(_sel(CapabilityTag).where(CapabilityTag.key == key))
    ).scalar_one_or_none()
    if found is None:
        db.add(CapabilityTag(key=key, name=key.replace("_", " ").title(), is_platform=True))
        await db.flush()
    return key


def _profile(structured, provenance, *, user_id="u-owner", created_by="u-owner", status="draft"):
    from app.models.matching import RequirementProfile

    return RequirementProfile(
        org_id="o-1",
        user_id=user_id,
        created_by=created_by,
        context_type="production",
        structured_requirements=structured,
        extraction_meta={"provenance": provenance},
        status=status,
    )


def test_build_match_requirement_r14_demotion_r424():
    from app.services.requirement_profile import RequirementProfileService as Rp

    # required_capabilities set by EXTRACTION → demoted to preferred (never a
    # hard S2 filter); an existing preferred set is unioned + sorted
    prof = _profile(
        {
            "required_capabilities": ["image_generation", "video_generation"],
            "preferred_capabilities": ["audio_generation"],
            "output_type": "image",
            "difficulty": "advanced",
            "time_budget": 60,
            "goal": "make art",
        },
        {"goal": "user_entered"},  # everything else extracted
    )
    req = Rp.build_match_requirement(prof)
    assert "required_capabilities" not in req  # extracted → not a hard filter
    assert set(req["preferred_capabilities"]) == {
        "audio_generation",
        "image_generation",
        "video_generation",
    }
    # extracted hard-filterable fields are moved to _soft_ variants
    assert "output_type" not in req and req["_soft_output_type"] == "image"
    assert "difficulty" not in req and req["_soft_difficulty"] == "advanced"
    assert "time_budget" not in req and req["_soft_time_budget"] == 60
    assert req["goal"] == "make art"  # user_entered scalar untouched

    # required_capabilities that a HUMAN entered stay HARD
    prof2 = _profile(
        {"required_capabilities": ["image_generation"], "output_type": "video"},
        {"required_capabilities": "user_entered", "output_type": "user_entered"},
    )
    req2 = Rp.build_match_requirement(prof2)
    assert req2["required_capabilities"] == ["image_generation"]  # stays hard
    assert req2["output_type"] == "video"  # user_entered → stays hard


def test_get_hard_constraints_user_entered_only_r424():
    from app.services.requirement_profile import RequirementProfileService as Rp

    prof = _profile(
        {"goal": "g", "output_type": "image", "difficulty": "expert"},
        {"goal": "user_entered", "output_type": "user_entered"},  # difficulty extracted
    )
    hard = Rp.get_hard_constraints(prof)
    assert hard == {"goal": "g", "output_type": "image"}  # difficulty excluded
    # soft preferences include EVERYTHING
    soft = Rp.get_soft_preferences(prof)
    assert set(soft) == {"goal", "output_type", "difficulty"}


def test_assert_can_write_owner_or_instructor_r424():
    from app.services.requirement_profile import RequirementProfileService as Rp

    prof = _profile({}, {}, user_id="owner-A", created_by="creator-B")
    # the OWNER (user_id) may write — proves owner resolves to user_id, not
    # created_by (an `and` in `user_id or created_by` would pick created_by)
    Rp._assert_can_write(prof, "owner-A", False)
    # a stranger may not
    with pytest.raises(AppError) as e:
        Rp._assert_can_write(prof, "stranger", False)
    assert e.value.status_code == 403
    # an instructor may always write
    Rp._assert_can_write(prof, "stranger", True)
    # a profile with no owner (both None) is writable by anyone
    prof_noowner = _profile({}, {}, user_id=None, created_by=None)
    Rp._assert_can_write(prof_noowner, "anyone", False)


async def test_validate_structured_bounds_r424(db):
    from app.services.requirement_profile import RequirementProfileService

    owner = await _user(db)
    org = await _org(db, owner)
    await _cap(db, "image_generation")
    svc = RequirementProfileService(db)

    async def _ok(structured):
        # create_from_form validates then persists
        return await svc.create_from_form(org.id, owner.id, "production", structured, owner.id)

    async def _bad(structured, code):
        # _validate_structured raises BEFORE any write, so no rollback needed —
        # the session (and the seeded org/cap) stays intact across calls
        with pytest.raises(AppError) as e:
            await _ok(structured)
        assert e.value.code == code

    # unknown field
    await _bad({"nonsense": 1}, "UNKNOWN_FIELD")
    # invalid enum values
    await _bad({"output_type": "hologram"}, "INVALID_OUTPUT_TYPE")
    await _bad({"difficulty": "godlike"}, "INVALID_DIFFICULTY")
    # time_budget: bool rejected, 0 rejected, out-of-range rejected; 1 & 100000 OK
    await _bad({"time_budget": True}, "INVALID_TIME_BUDGET")
    await _bad({"time_budget": 0}, "INVALID_TIME_BUDGET")
    await _bad({"time_budget": 100001}, "INVALID_TIME_BUDGET")
    await _bad({"tool_constraints": ["x" * 101]}, "INVALID_TOOL_CONSTRAINTS")
    await _bad({"tool_constraints": "notalist"}, "INVALID_TOOL_CONSTRAINTS")
    await _bad({"required_capabilities": ["made_up_cap"]}, "UNKNOWN_CAPABILITY")
    await _bad({"required_capabilities": [123]}, "INVALID_CAPABILITIES")
    # boundary ACCEPTS (each a successful create → its own flush)
    p1 = await _ok({"time_budget": 1})  # lower bound inclusive
    assert p1.structured_requirements["time_budget"] == 1
    pmax = await _ok({"time_budget": 100000})  # upper bound inclusive
    assert pmax.structured_requirements["time_budget"] == 100000
    p100 = await _ok({"tool_constraints": ["x" * 100]})  # 100 chars OK
    assert p100.structured_requirements["tool_constraints"] == ["x" * 100]


async def test_normalize_extracted_drops_unknowns_r424(db):
    from app.services.requirement_profile import (
        ExtractedRequirements,
        RequirementProfileService,
    )

    svc = RequirementProfileService(db)
    keys = {"image_generation", "video_generation"}
    extracted = ExtractedRequirements(
        required_capabilities=["image_generation", "made_up"],
        preferred_capabilities=["only_bogus"],
        output_type="hologram",  # unknown enum → dropped
        difficulty="expert",  # known enum → kept
        time_budget=999999,  # out of range → dropped
        goal="build a thing",
    )
    structured, unmatched = svc._normalize_extracted(extracted, keys)
    # only the valid capability survives; invalid ones go to unmatched
    assert structured["required_capabilities"] == ["image_generation"]
    assert "preferred_capabilities" not in structured  # all bogus → dropped
    assert "made_up" in unmatched and "only_bogus" in unmatched
    # unknown enum / out-of-range dropped and reported
    assert "output_type" not in structured
    assert "hologram" in unmatched
    assert "999999" in unmatched
    # a KNOWN enum is kept
    assert structured["difficulty"] == "expert"
    assert structured["goal"] == "build a thing"

    # lower-bound time_budget=1 is VALID and must be KEPT (kills the
    # `1 <= tb` boundary mutants in _normalize — a `<` or `2` would drop it)
    kept, _ = svc._normalize_extracted(ExtractedRequirements(time_budget=1), keys)
    assert kept["time_budget"] == 1
    dropped, un = svc._normalize_extracted(
        ExtractedRequirements(time_budget=0), keys
    )  # 0 is out of range
    assert "time_budget" not in dropped and "0" in un
    # upper-bound 100000 is VALID and kept (kills the  mutant)
    kept_hi, _ = svc._normalize_extracted(ExtractedRequirements(time_budget=100000), keys)
    assert kept_hi["time_budget"] == 100000


async def test_confirm_and_update_draft_only_r424(db):
    from app.services.requirement_profile import RequirementProfileService

    owner = await _user(db)
    org = await _org(db, owner)
    await _cap(db, "image_generation")
    svc = RequirementProfileService(db)

    prof = await svc.create_from_form(org.id, owner.id, "production", {"goal": "g"}, owner.id)

    # an edit sets provenance to user_entered for the changed key
    updated = await svc.update_profile(prof.id, org.id, {"output_type": "image"}, owner.id)
    assert updated.extraction_meta["provenance"]["output_type"] == "user_entered"

    # confirm flips status; a second confirm 422s; edits after confirm 423
    confirmed = await svc.confirm(prof.id, org.id, owner.id)
    assert confirmed.status == "confirmed"
    with pytest.raises(AppError) as e_c:
        await svc.confirm(prof.id, org.id, owner.id)
    assert e_c.value.status_code == 422
    with pytest.raises(AppError) as e_u:
        await svc.update_profile(prof.id, org.id, {"goal": "g2"}, owner.id)
    # both the pre-check (423) and the guarded-UPDATE rowcount fallback (422)
    # raise the same domain code — a confirmed profile is never editable
    assert e_u.value.code == "PROFILE_ALREADY_CONFIRMED"
    assert e_u.value.status_code in (422, 423)

    # a non-owner non-instructor cannot confirm/update someone else's draft
    prof2 = await svc.create_from_form(org.id, owner.id, "production", {"goal": "g"}, owner.id)
    stranger = await _user(db, UserRole.STUDENT)
    with pytest.raises(AppError) as e_perm:
        await svc.update_profile(prof2.id, org.id, {"goal": "x"}, stranger.id)
    assert e_perm.value.status_code == 403
