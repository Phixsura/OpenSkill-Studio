"""Tests for Request Transformation Pipeline service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_transform_pipeline import (
    TransformPipeline, Transform,
)


class TestTransformPipeline:
    def test_rename_field(self):
        svc = TransformPipeline()
        svc.create_pipeline("p1")
        svc.add_transform("p1", Transform("t1", "Rename", "rename_field",
                                           {"from": "user_name", "to": "username"}))
        result = svc.execute("p1", {"user_name": "alice", "age": 30})
        assert result["data"] == {"username": "alice", "age": 30}
        assert result["transform_count"] == 1

    def test_remove_field(self):
        svc = TransformPipeline()
        svc.create_pipeline("p1")
        svc.add_transform("p1", Transform("t1", "Remove PW", "remove_field", {"field": "password"}))
        result = svc.execute("p1", {"name": "bob", "password": "secret"})
        assert "password" not in result["data"]

    def test_add_field(self):
        svc = TransformPipeline()
        svc.create_pipeline("p1")
        svc.add_transform("p1", Transform("t1", "Add Version", "add_field",
                                           {"field": "api_version", "value": "v2"}))
        result = svc.execute("p1", {"data": 1})
        assert result["data"]["api_version"] == "v2"

    def test_map_value(self):
        svc = TransformPipeline()
        svc.create_pipeline("p1")
        svc.add_transform("p1", Transform("t1", "Map Status", "map_value",
                                           {"field": "status", "mapping": {"1": "active", "0": "inactive"}}))
        result = svc.execute("p1", {"status": "1"})
        assert result["data"]["status"] == "active"

    def test_filter_keys(self):
        svc = TransformPipeline()
        svc.create_pipeline("p1")
        svc.add_transform("p1", Transform("t1", "Filter", "filter_keys",
                                           {"keys": ["name", "email"]}))
        result = svc.execute("p1", {"name": "a", "email": "b", "secret": "c"})
        assert result["data"] == {"name": "a", "email": "b"}

    def test_chain_transforms(self):
        svc = TransformPipeline()
        svc.create_pipeline("p1")
        svc.add_transform("p1", Transform("t1", "Rename", "rename_field", {"from": "nm", "to": "name"}))
        svc.add_transform("p1", Transform("t2", "Add", "add_field", {"field": "source", "value": "api"}))
        result = svc.execute("p1", {"nm": "test"})
        assert result["data"] == {"name": "test", "source": "api"}
        assert result["transform_count"] == 2

    def test_disabled_transform_skipped(self):
        svc = TransformPipeline()
        svc.create_pipeline("p1")
        svc.add_transform("p1", Transform("t1", "X", "add_field", {"field": "x", "value": 1}, enabled=False))
        result = svc.execute("p1", {"a": 1})
        assert "x" not in result["data"]

    def test_remove_transform(self):
        svc = TransformPipeline()
        svc.create_pipeline("p1")
        svc.add_transform("p1", Transform("t1", "X", "add_field", {"field": "x", "value": 1}))
        svc.remove_transform("p1", "t1")
        assert svc.get_pipeline("p1") == []

    def test_duplicate_pipeline(self):
        svc = TransformPipeline()
        svc.create_pipeline("p1")
        with pytest.raises(ValueError):
            svc.create_pipeline("p1")

    def test_invalid_kind(self):
        svc = TransformPipeline()
        svc.create_pipeline("p1")
        with pytest.raises(ValueError):
            svc.add_transform("p1", Transform("t1", "X", "invalid_kind"))

    def test_isolation(self):
        a, b = TransformPipeline(), TransformPipeline()
        a.create_pipeline("p1")
        with pytest.raises(ValueError):
            b.execute("p1", {})
