from app.services.app_marketplace_extension_dep_conflict import (
    DepConflictResolverService, DepRequirement, version_satisfies
)


def test_caret_constraint():
    assert version_satisfies("1.5.0", "^1.2.0") is True
    assert version_satisfies("2.0.0", "^1.2.0") is False
    assert version_satisfies("1.1.0", "^1.2.0") is False
    # ^0.x.y is minor-locked
    assert version_satisfies("0.2.5", "^0.2.0") is True
    assert version_satisfies("0.3.0", "^0.2.0") is False


def test_tilde_constraint():
    assert version_satisfies("1.2.5", "~1.2.0") is True
    assert version_satisfies("1.3.0", "~1.2.0") is False
    assert version_satisfies("1.2.0", "~1.2.3") is False


def test_comparison_constraints():
    assert version_satisfies("2.0.0", ">=1.5.0") is True
    assert version_satisfies("1.4.0", ">=1.5.0") is False
    assert version_satisfies("1.0.0", "<2.0.0") is True
    assert version_satisfies("2.0.0", "<2.0.0") is False


def test_exact_match():
    assert version_satisfies("1.2.3", "1.2.3") is True
    assert version_satisfies("1.2.4", "1.2.3") is False


def test_no_conflict():
    svc = DepConflictResolverService()
    svc.register_versions("lodash", ["4.17.0", "4.17.1", "4.17.21"])
    reqs = [
        DepRequirement("lodash", "^4.17.0", "ext-a"),
        DepRequirement("lodash", "^4.17.1", "ext-b"),
    ]
    conflicts = svc.detect_conflicts(reqs)
    assert len(conflicts) == 0


def test_detect_diamond_conflict():
    svc = DepConflictResolverService()
    svc.register_versions("react", ["16.14.0", "17.0.2", "18.2.0"])
    reqs = [
        DepRequirement("react", "^16.0.0", "ext-a"),  # needs 16.x
        DepRequirement("react", "^18.0.0", "ext-b"),  # needs 18.x
    ]
    conflicts = svc.detect_conflicts(reqs)
    assert len(conflicts) == 1
    assert "react" in conflicts[0].reason


def test_resolve_newest():
    svc = DepConflictResolverService()
    svc.register_versions("axios", ["0.21.0", "0.27.0", "1.0.0", "1.4.0", "1.5.0"])
    reqs = [
        DepRequirement("axios", "^1.0.0", "ext-a"),
        DepRequirement("axios", ">=1.2.0", "ext-b"),
    ]
    resolutions = svc.resolve(reqs, "newest")
    assert resolutions[0].version == "1.5.0"


def test_resolve_oldest():
    svc = DepConflictResolverService()
    svc.register_versions("express", ["4.17.0", "4.18.0", "4.18.2"])
    reqs = [DepRequirement("express", "^4.17.0", "ext-a")]
    resolutions = svc.resolve(reqs, "oldest")
    assert resolutions[0].version == "4.17.0"


def test_resolve_force_on_conflict():
    svc = DepConflictResolverService()
    svc.register_versions("lib", ["1.0.0", "2.0.0", "3.0.0"])
    reqs = [
        DepRequirement("lib", "^1.0.0", "ext-a"),
        DepRequirement("lib", "^2.0.0", "ext-b"),
    ]
    # No common version — force picks the one satisfying the most
    resolutions = svc.resolve(reqs, "newest")
    assert resolutions[0].strategy == "force"
    # Should pick 2.0.0 or 3.0.0 (satisfies ext-b's ^2.0.0)
    assert resolutions[0].version in ("2.0.0", "3.0.0")
