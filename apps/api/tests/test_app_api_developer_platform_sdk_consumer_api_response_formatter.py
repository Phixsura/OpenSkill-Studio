"""Tests for Consumer API Response Formatter service."""
import json
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_response_formatter import ResponseFormatter


class TestResponseFormatter:
    def test_json_format(self):
        svc = ResponseFormatter()
        result = svc.format({"id": 1, "name": "Alice"})
        assert result["content_type"] == "application/json"
        parsed = json.loads(result["body"])
        assert parsed["data"]["id"] == 1

    def test_json_with_meta(self):
        svc = ResponseFormatter()
        result = svc.format([{"id": 1}], meta={"total": 1})
        parsed = json.loads(result["body"])
        assert parsed["meta"]["total"] == 1

    def test_csv_format(self):
        svc = ResponseFormatter()
        result = svc.format([{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}], fmt="csv")
        assert result["content_type"] == "text/csv"
        assert "id,name" in result["body"]
        assert "Alice" in result["body"]

    def test_xml_format(self):
        svc = ResponseFormatter()
        result = svc.format({"id": 1}, fmt="xml")
        assert result["content_type"] == "application/xml"
        assert "<id>1</id>" in result["body"]

    def test_yaml_format(self):
        svc = ResponseFormatter()
        result = svc.format({"key": "value"}, fmt="yaml")
        assert result["content_type"] == "application/yaml"
        assert "key: value" in result["body"]

    def test_no_envelope(self):
        svc = ResponseFormatter()
        svc.configure(wrap_in_envelope=False)
        result = svc.format({"id": 1})
        parsed = json.loads(result["body"])
        assert "data" not in parsed
        assert parsed["id"] == 1

    def test_pretty_print(self):
        svc = ResponseFormatter()
        svc.configure(pretty_print=True)
        result = svc.format({"id": 1})
        assert "\n" in result["body"]

    def test_content_negotiation(self):
        svc = ResponseFormatter()
        assert svc.negotiate("application/xml") == "xml"
        assert svc.negotiate("text/csv") == "csv"
        assert svc.negotiate("application/json") == "json"

    def test_stats(self):
        svc = ResponseFormatter()
        svc.format({"a": 1})
        svc.format({"b": 2}, fmt="csv")
        stats = svc.get_stats()
        assert stats["total_formatted"] == 2
        assert stats["format_counts"]["json"] == 1

    def test_invalid_format(self):
        svc = ResponseFormatter()
        with pytest.raises(ValueError):
            svc.format({}, fmt="protobuf")

    def test_isolation(self):
        a, b = ResponseFormatter(), ResponseFormatter()
        a.format({"x": 1})
        assert b.get_stats()["total_formatted"] == 0
