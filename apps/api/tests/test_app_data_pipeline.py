"""Tests for App Data Pipeline — stages, execution, failure, skipping."""

import pytest

from app.services.app_data_pipeline import AppDataPipeline, StageStatus

STAGES = [
    {"stage_id": "extract", "name": "Extract Data", "type": "extract"},
    {"stage_id": "transform", "name": "Transform", "type": "transform"},
    {"stage_id": "load", "name": "Load to DB", "type": "load"},
]


class TestCreatePipeline:
    def test_create(self):
        p = AppDataPipeline()
        pl = p.create_pipeline("inst-1", "p1", "ETL Job", STAGES)
        assert pl.pipeline_id == "p1"
        assert len(pl.stages) == 3
        assert pl.status == "pending"

    def test_empty_stages(self):
        p = AppDataPipeline()
        with pytest.raises(ValueError, match="at least one"):
            p.create_pipeline("inst-1", "p1", "Empty", [])

    def test_duplicate(self):
        p = AppDataPipeline()
        p.create_pipeline("inst-1", "p1", "Job", STAGES)
        with pytest.raises(ValueError, match="already exists"):
            p.create_pipeline("inst-1", "p1", "Job2", STAGES)


class TestStageExecution:
    def test_start_stage(self):
        p = AppDataPipeline()
        p.create_pipeline("inst-1", "p1", "Job", STAGES)
        s = p.start_stage("inst-1", "p1", "extract", input_count=100, now=1000.0)
        assert s.status == StageStatus.RUNNING
        assert s.input_count == 100

    def test_complete_stage(self):
        p = AppDataPipeline()
        p.create_pipeline("inst-1", "p1", "Job", STAGES)
        p.start_stage("inst-1", "p1", "extract", now=1000.0)
        s = p.complete_stage("inst-1", "p1", "extract", output_count=95, now=1002.0)
        assert s.status == StageStatus.COMPLETED
        assert s.output_count == 95
        assert s.duration_ms == 2000.0

    def test_full_pipeline(self):
        p = AppDataPipeline()
        p.create_pipeline("inst-1", "p1", "Job", STAGES)
        for sid in ["extract", "transform", "load"]:
            p.start_stage("inst-1", "p1", sid)
            p.complete_stage("inst-1", "p1", sid)
        pl = p.get_pipeline("inst-1", "p1")
        assert pl.status == "completed"

    def test_cannot_start_running(self):
        p = AppDataPipeline()
        p.create_pipeline("inst-1", "p1", "Job", STAGES)
        p.start_stage("inst-1", "p1", "extract")
        with pytest.raises(ValueError, match="Cannot start"):
            p.start_stage("inst-1", "p1", "extract")


class TestFailure:
    def test_fail_stage(self):
        p = AppDataPipeline()
        p.create_pipeline("inst-1", "p1", "Job", STAGES)
        p.start_stage("inst-1", "p1", "extract", now=1000.0)
        s = p.fail_stage("inst-1", "p1", "extract", error="connection lost", now=1001.0)
        assert s.status == StageStatus.FAILED
        assert s.error == "connection lost"

    def test_remaining_stages_skipped(self):
        p = AppDataPipeline()
        p.create_pipeline("inst-1", "p1", "Job", STAGES)
        p.start_stage("inst-1", "p1", "extract")
        p.fail_stage("inst-1", "p1", "extract")
        pl = p.get_pipeline("inst-1", "p1")
        assert pl.stages[1].status == StageStatus.SKIPPED
        assert pl.stages[2].status == StageStatus.SKIPPED
        assert pl.status == "failed"


class TestCurrentStage:
    def test_current_stage(self):
        p = AppDataPipeline()
        p.create_pipeline("inst-1", "p1", "Job", STAGES)
        pl = p.get_pipeline("inst-1", "p1")
        assert pl.current_stage is not None
        assert pl.current_stage.stage_id == "extract"

    def test_no_current_when_done(self):
        p = AppDataPipeline()
        p.create_pipeline("inst-1", "p1", "Job", STAGES)
        for sid in ["extract", "transform", "load"]:
            p.start_stage("inst-1", "p1", sid)
            p.complete_stage("inst-1", "p1", sid)
        pl = p.get_pipeline("inst-1", "p1")
        assert pl.current_stage is None


class TestIsolation:
    def test_cross_installation(self):
        p = AppDataPipeline()
        p.create_pipeline("inst-1", "p1", "Job", STAGES)
        with pytest.raises(KeyError):
            p.get_pipeline("inst-2", "p1")
