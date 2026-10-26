from app.services.app_marketplace_extension_build_pipeline import (
    BuildPipelineService, BuildStatus, StageType,
)


def test_create_build():
    svc = BuildPipelineService()
    build = svc.create_build("ext-1", "1.0.0")
    assert build.status == BuildStatus.QUEUED
    assert len(build.stages) == 5


def test_start_build():
    svc = BuildPipelineService()
    build = svc.create_build("ext-1", "1.0.0")
    assert svc.start_build(build.build_id) is True
    assert build.status == BuildStatus.RUNNING
    assert build.stages[0].status == BuildStatus.RUNNING


def test_complete_all_stages():
    svc = BuildPipelineService()
    build = svc.create_build("ext-1", "1.0.0", stages=[StageType.LINT, StageType.TEST])
    svc.start_build(build.build_id)
    svc.complete_stage(build.build_id, 0, True, duration_ms=500)
    assert build.stages[1].status == BuildStatus.RUNNING
    svc.complete_stage(build.build_id, 1, True, duration_ms=2000)
    assert build.status == BuildStatus.PASSED
    assert build.artifact_url != ""


def test_stage_failure_stops_build():
    svc = BuildPipelineService()
    build = svc.create_build("ext-1", "1.0.0", stages=[StageType.LINT, StageType.TEST])
    svc.start_build(build.build_id)
    result = svc.complete_stage(build.build_id, 0, False, log="syntax error")
    assert result["build_status"] == "failed"
    assert build.stages[1].status == BuildStatus.QUEUED  # never started


def test_cancel():
    svc = BuildPipelineService()
    build = svc.create_build("ext-1", "1.0.0")
    svc.start_build(build.build_id)
    assert svc.cancel_build(build.build_id) is True
    assert build.status == BuildStatus.CANCELLED


def test_build_stats():
    svc = BuildPipelineService()
    b1 = svc.create_build("ext-1", "1.0.0", stages=[StageType.LINT])
    svc.start_build(b1.build_id)
    svc.complete_stage(b1.build_id, 0, True)
    b2 = svc.create_build("ext-1", "1.0.1", stages=[StageType.LINT])
    svc.start_build(b2.build_id)
    svc.complete_stage(b2.build_id, 0, False)
    stats = svc.get_stats("ext-1")
    assert stats["pass_rate"] == 50.0


def test_custom_stages():
    svc = BuildPipelineService()
    build = svc.create_build("ext-1", "1.0.0",
                             stages=[StageType.TEST, StageType.PACKAGE, StageType.PUBLISH])
    assert len(build.stages) == 3
    assert build.stages[2].stage_type == StageType.PUBLISH
