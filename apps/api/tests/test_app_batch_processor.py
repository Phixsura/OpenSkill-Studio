"""Tests for App Batch Processor — create, process, progress, completion."""

import pytest

from app.services.app_batch_processor import (
    AppBatchProcessor,
    BatchStatus,
    ItemResult,
)


class TestCreateBatch:
    def test_create(self):
        p = AppBatchProcessor()
        b = p.create_batch("inst-1", "b1", [{"x": 1}, {"x": 2}])
        assert b.batch_id == "b1"
        assert b.total == 2
        assert b.status == BatchStatus.QUEUED

    def test_empty_items(self):
        p = AppBatchProcessor()
        with pytest.raises(ValueError, match="at least one"):
            p.create_batch("inst-1", "b1", [])

    def test_duplicate(self):
        p = AppBatchProcessor()
        p.create_batch("inst-1", "b1", [{"x": 1}])
        with pytest.raises(ValueError, match="already exists"):
            p.create_batch("inst-1", "b1", [{"x": 2}])

    def test_item_ids_generated(self):
        p = AppBatchProcessor()
        b = p.create_batch("inst-1", "b1", [{"a": 1}, {"b": 2}])
        assert b.items[0].item_id == "b1-0"
        assert b.items[1].item_id == "b1-1"


class TestLifecycle:
    def test_start(self):
        p = AppBatchProcessor()
        p.create_batch("inst-1", "b1", [{"x": 1}])
        b = p.start_batch("inst-1", "b1")
        assert b.status == BatchStatus.PROCESSING
        assert b.started_at is not None

    def test_cannot_start_processing(self):
        p = AppBatchProcessor()
        p.create_batch("inst-1", "b1", [{"x": 1}])
        p.start_batch("inst-1", "b1")
        with pytest.raises(ValueError, match="Cannot start"):
            p.start_batch("inst-1", "b1")

    def test_complete_all_success(self):
        p = AppBatchProcessor()
        p.create_batch("inst-1", "b1", [{"x": 1}])
        p.start_batch("inst-1", "b1")
        p.record_item_result("inst-1", "b1", "b1-0", ItemResult.SUCCESS)
        b = p.complete_batch("inst-1", "b1")
        assert b.status == BatchStatus.COMPLETED

    def test_complete_all_failed(self):
        p = AppBatchProcessor()
        p.create_batch("inst-1", "b1", [{"x": 1}])
        p.start_batch("inst-1", "b1")
        p.record_item_result("inst-1", "b1", "b1-0", ItemResult.FAILED, error="boom")
        b = p.complete_batch("inst-1", "b1")
        assert b.status == BatchStatus.FAILED

    def test_partial_failure(self):
        p = AppBatchProcessor()
        p.create_batch("inst-1", "b1", [{"x": 1}, {"x": 2}])
        p.start_batch("inst-1", "b1")
        p.record_item_result("inst-1", "b1", "b1-0", ItemResult.SUCCESS)
        p.record_item_result("inst-1", "b1", "b1-1", ItemResult.FAILED)
        b = p.complete_batch("inst-1", "b1")
        assert b.status == BatchStatus.PARTIALLY_FAILED


class TestProgress:
    def test_progress(self):
        p = AppBatchProcessor()
        p.create_batch("inst-1", "b1", [{"x": i} for i in range(4)])
        p.start_batch("inst-1", "b1")
        p.record_item_result("inst-1", "b1", "b1-0", ItemResult.SUCCESS)
        p.record_item_result("inst-1", "b1", "b1-1", ItemResult.SUCCESS)
        prog = p.get_progress("inst-1", "b1")
        assert prog["total"] == 4
        assert prog["processed"] == 2
        assert prog["succeeded"] == 2
        assert prog["progress_pct"] == 50.0


class TestItemResult:
    def test_record_unknown_item(self):
        p = AppBatchProcessor()
        p.create_batch("inst-1", "b1", [{"x": 1}])
        with pytest.raises(KeyError, match="Item"):
            p.record_item_result("inst-1", "b1", "nope", ItemResult.SUCCESS)


class TestIsolation:
    def test_cross_installation(self):
        p = AppBatchProcessor()
        p.create_batch("inst-1", "b1", [{"x": 1}])
        with pytest.raises(KeyError):
            p.get_batch("inst-2", "b1")
