from app.services.app_marketplace_extension_sandbox_error_reporter import (
    SandboxErrorReporterService,
)


def test_report_and_group():
    svc = SandboxErrorReporterService()
    svc.report("sb-1", "undefined is not a function", "TypeError", file="app.js", line=42)
    svc.report("sb-1", "undefined is not a function", "TypeError", file="app.js", line=42)
    groups = svc.get_groups("sb-1")
    assert len(groups) == 1
    assert groups[0].count == 2


def test_different_errors_separate_groups():
    svc = SandboxErrorReporterService()
    svc.report("sb-1", "null ref", "TypeError", file="a.js", line=1)
    svc.report("sb-1", "divide by zero", "ArithmeticError", file="b.js", line=5)
    groups = svc.get_groups("sb-1")
    assert len(groups) == 2


def test_resolve():
    svc = SandboxErrorReporterService()
    svc.report("sb-1", "bug", "Error", file="x.js", line=1)
    groups = svc.get_groups("sb-1")
    fp = groups[0].fingerprint
    assert svc.resolve("sb-1", fp) is True
    unresolved = svc.get_groups("sb-1", unresolved_only=True)
    assert len(unresolved) == 0


def test_re_report_unresolves():
    svc = SandboxErrorReporterService()
    svc.report("sb-1", "bug", "Error", file="x.js", line=1)
    groups = svc.get_groups("sb-1")
    svc.resolve("sb-1", groups[0].fingerprint)
    svc.report("sb-1", "bug", "Error", file="x.js", line=1)
    groups2 = svc.get_groups("sb-1", unresolved_only=True)
    assert len(groups2) == 1  # re-opened


def test_top_errors():
    svc = SandboxErrorReporterService()
    for _ in range(10):
        svc.report("sb-1", "common", "Error", file="a.js", line=1)
    for _ in range(3):
        svc.report("sb-1", "rare", "Error", file="b.js", line=2)
    top = svc.get_top_errors("sb-1", 1)
    assert top[0].message == "common"
    assert top[0].count == 10


def test_stats():
    svc = SandboxErrorReporterService()
    svc.report("sb-1", "a", "E", file="x", line=1)
    svc.report("sb-1", "a", "E", file="x", line=1)
    svc.report("sb-1", "b", "E", file="y", line=2)
    stats = svc.get_stats("sb-1")
    assert stats["total_errors"] == 3
    assert stats["unique_errors"] == 2
    assert stats["unresolved"] == 2


def test_error_rate():
    svc = SandboxErrorReporterService()
    for _ in range(5):
        svc.report("sb-1", "err", "E")
    rate = svc.get_error_rate("sb-1", window_seconds=60)
    assert rate["count"] == 5
    assert rate["rate_per_minute"] == 5.0
