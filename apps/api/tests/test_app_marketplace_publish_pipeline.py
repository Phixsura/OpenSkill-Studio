from app.services.app_marketplace_publish_pipeline import PublishPipeline, StageResult


def test_successful_pipeline():
    pp = PublishPipeline()
    result = pp.run("r1", "ext-1", "1.0.0", {
        "name": "My Extension",
        "description": "A useful extension for developers to use",
        "code": "def hello(): return 'world'",
    })
    assert result.overall_result == "success"
    assert len(result.stages) == 5
    assert all(s.result == StageResult.PASSED for s in result.stages)


def test_validation_failure():
    pp = PublishPipeline()
    result = pp.run("r2", "ext-2", "1.0.0", {"name": "", "description": ""})
    assert result.overall_result == "failed"
    assert result.stages[0].result == StageResult.FAILED
    assert len(result.stages) == 1  # stopped after first failure


def test_security_failure():
    pp = PublishPipeline()
    result = pp.run("r3", "ext-3", "1.0.0", {
        "name": "Bad Extension",
        "description": "This extension does bad things to your system",
        "code": "result = eval(user_input)",
    })
    assert result.overall_result == "failed"
    security_stage = next(s for s in result.stages if s.stage.value == "security_scan")
    assert security_stage.result == StageResult.FAILED
    assert any("eval" in i for i in security_stage.details["issues"])


def test_get_and_list_runs():
    pp = PublishPipeline()
    pp.run("r10", "ext-a", "1.0.0", {"name": "A", "description": "A decent description here"})
    pp.run("r11", "ext-a", "1.1.0", {"name": "A", "description": "Another good description"})
    assert pp.get_run("r10") is not None
    assert len(pp.list_runs("ext-a")) == 2


def test_pipeline_has_timing():
    pp = PublishPipeline()
    result = pp.run("r20", "ext-t", "1.0.0", {
        "name": "Timed", "description": "An extension with timing data included",
    })
    assert result.started_at != ""
    assert result.finished_at != ""
