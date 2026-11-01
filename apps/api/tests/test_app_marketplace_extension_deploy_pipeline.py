from app.services.app_marketplace_extension_deploy_pipeline import ExtDeployPipelineService

def test_create_pipeline():
    svc = ExtDeployPipelineService()
    p = svc.create("ext-1", "1.0.0")
    assert len(p.stages) == 5
    assert p.status == "pending"

def test_full_pipeline():
    svc = ExtDeployPipelineService()
    p = svc.create("ext-1", "1.0.0")
    for stage in ["lint", "test", "build", "security-scan", "deploy"]:
        svc.run_stage(p.pipeline_id, stage)
    assert p.status == "passed"

def test_failed_pipeline():
    svc = ExtDeployPipelineService()
    p = svc.create("ext-1", "1.0.0")
    svc.run_stage(p.pipeline_id, "lint")
    svc.run_stage(p.pipeline_id, "test", passed=False, output="3 tests failed")
    assert p.status == "failed"
    # Remaining stages skipped
    assert sum(1 for s in p.stages if s.status == "skipped") == 3
