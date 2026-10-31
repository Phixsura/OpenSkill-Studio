from app.services.app_marketplace_ci_integration import (
    CIIntegration, BuildStatus,
)


def test_create_build():
    ci = CIIntegration()
    build = ci.create_build("b1", "ext-1", "1.0.0", "push", "main", "abc123")
    assert build.status == BuildStatus.RUNNING
    assert len(build.steps) == 5
    assert build.steps[0].name == "install"


def test_update_steps_and_finish():
    ci = CIIntegration()
    ci.create_build("b2", "ext-2", "1.0.0", "pr", "feature", "def456")
    for step in ["install", "lint", "test", "build", "security_scan"]:
        ci.update_step("b2", step, BuildStatus.PASSED, 100.0)
    build = ci.finish_build("b2")
    assert build.status == BuildStatus.PASSED


def test_failed_build():
    ci = CIIntegration()
    ci.create_build("b3", "ext-3", "1.0.0", "push", "main", "ghi789")
    ci.update_step("b3", "install", BuildStatus.PASSED, 50.0)
    ci.update_step("b3", "lint", BuildStatus.FAILED, 20.0, log="Lint errors found")
    build = ci.finish_build("b3")
    assert build.status == BuildStatus.FAILED


def test_artifacts():
    ci = CIIntegration()
    ci.create_build("b4", "ext-4", "1.0.0", "manual", "main", "xyz")
    ci.add_artifact("b4", "dist/ext-4-1.0.0.tar.gz")
    ci.add_artifact("b4", "coverage/report.html")
    build = ci.get_build("b4")
    assert len(build.artifacts) == 2


def test_list_builds():
    ci = CIIntegration()
    ci.create_build("b10", "ext-a", "1.0.0", "push", "main", "a1")
    ci.create_build("b11", "ext-a", "1.1.0", "push", "main", "a2")
    ci.create_build("b12", "ext-b", "1.0.0", "push", "main", "b1")
    assert len(ci.list_builds("ext-a")) == 2


def test_build_summary():
    ci = CIIntegration()
    ci.create_build("b20", "ext-s", "1.0.0", "push", "main", "s1")
    ci.update_step("b20", "install", BuildStatus.PASSED, 100.0)
    ci.update_step("b20", "lint", BuildStatus.PASSED, 50.0)
    ci.add_artifact("b20", "dist/pkg.tar.gz")
    summary = ci.get_build_summary("b20")
    assert summary["passed"] == 2
    assert summary["total_duration_ms"] == 150.0
    assert summary["artifacts"] == 1
