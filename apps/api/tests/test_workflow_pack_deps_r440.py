"""R440: workflow_pack._validate_dependencies — untrusted manifest hardening (R7).

Type-checks every dependency entry before len()/iteration so arbitrary JSON
(ints, strings, dicts, over-length) 422s instead of TypeError-ing into a 500.
Pure static → fast, no DB.
"""

import pytest

from app.exceptions import AppError
from app.services.workflow_pack import MAX_DEPENDENCIES
from app.services.workflow_pack import WorkflowPackService as Wp


def _ok(deps):
    Wp._validate_dependencies(deps)  # must not raise


def _bad(deps, code=None):
    with pytest.raises(AppError) as e:
        Wp._validate_dependencies(deps)
    if code:
        assert e.value.code == code
    assert e.value.status_code == 422


def test_valid_dependencies_r440():
    _ok({})  # empty is fine
    _ok({"requires_capabilities": [], "recommended_packs": []})
    _ok({
        "requires_capabilities": [
            {"capability": "image_generation"},
            {"capability": "upscale", "features": ["hd", "4k"]},
        ],
        "recommended_packs": [
            {"family": "skill_pack", "slug": "foundations"},
            {"family": "workflow_pack", "version": ">=1.2.0"},
            {"family": "workflow_pack", "version": "2.0.0"},
        ],
    })


def test_top_level_type_and_count_r440():
    _bad({"requires_capabilities": "notalist"})
    _bad({"recommended_packs": {"not": "a list"}})
    # count cap is over the SUM of both lists
    caps = [{"capability": f"c{i}"} for i in range(MAX_DEPENDENCIES)]
    _ok({"requires_capabilities": caps})  # exactly MAX is allowed
    _bad({"requires_capabilities": caps, "recommended_packs": [{"family": "skill_pack"}]},
         "TOO_MANY_DEPENDENCIES")


def test_capability_entry_validation_r440():
    _bad({"requires_capabilities": ["notadict"]})
    _bad({"requires_capabilities": [{"capability": 123}]})     # non-string
    _bad({"requires_capabilities": [{"capability": ""}]})      # empty
    _bad({"requires_capabilities": [{"capability": "x" * 65}]})  # over 64
    _ok({"requires_capabilities": [{"capability": "x" * 64}]})   # exactly 64 OK
    # features: non-list, too many, non-string, over-length
    _bad({"requires_capabilities": [{"capability": "c", "features": "hd"}]})
    _bad({"requires_capabilities": [{"capability": "c", "features": ["f"] * 21}]})  # 21 valid strings
    _ok({"requires_capabilities": [{"capability": "c", "features": ["f"] * 20}]})  # exactly 20
    _bad({"requires_capabilities": [{"capability": "c", "features": [123]}]})       # non-string
    _bad({"requires_capabilities": [{"capability": "c", "features": ["x" * 65]}]})  # over 64
    _ok({"requires_capabilities": [{"capability": "c", "features": ["x" * 64]}]})   # 64 OK


def test_recommended_pack_validation_r440():
    _bad({"recommended_packs": ["notadict"]})
    _bad({"recommended_packs": [{"family": "bogus"}]})            # bad family
    _bad({"recommended_packs": [{}]})                            # missing family
    # version constraint: bad format, non-string
    _bad({"recommended_packs": [{"family": "skill_pack", "version": "1.2"}]},
         "INVALID_VERSION_CONSTRAINT")
    _bad({"recommended_packs": [{"family": "skill_pack", "version": 123}]},
         "INVALID_VERSION_CONSTRAINT")
    _ok({"recommended_packs": [{"family": "skill_pack", "version": ">=1.0.0"}]})
    _ok({"recommended_packs": [{"family": "skill_pack", "version": "1.0.0"}]})
    _ok({"recommended_packs": [{"family": "skill_pack"}]})        # version optional
    # slug: non-string / over-length
    _bad({"recommended_packs": [{"family": "skill_pack", "slug": "x" * 201}]})
    _bad({"recommended_packs": [{"family": "skill_pack", "slug": 123}]})
    _ok({"recommended_packs": [{"family": "skill_pack", "slug": "x" * 200}]})  # 200 OK
