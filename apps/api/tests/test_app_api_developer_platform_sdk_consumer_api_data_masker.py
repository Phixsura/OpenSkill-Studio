"""Tests for Consumer API Data Masker service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_data_masker import (
    DataMasker, MaskRule,
)


class TestDataMasker:
    def test_full_mask(self):
        svc = DataMasker()
        svc.add_rule(MaskRule("r1", "password", "full", "***"))
        result = svc.mask({"password": "secret123", "name": "Alice"})
        assert result["data"]["password"] == "***"
        assert result["data"]["name"] == "Alice"

    def test_partial_mask(self):
        svc = DataMasker()
        svc.add_rule(MaskRule("r1", "email", "partial"))
        result = svc.mask({"email": "alice@example.com"})
        masked = result["data"]["email"]
        assert masked.startswith("al")
        assert masked.endswith("om")
        assert "*" in masked

    def test_hash_mask(self):
        svc = DataMasker()
        svc.add_rule(MaskRule("r1", "ssn", "hash"))
        result = svc.mask({"ssn": "123-45-6789"})
        assert result["data"]["ssn"] != "123-45-6789"
        assert len(result["data"]["ssn"]) == 16

    def test_redact_mask(self):
        svc = DataMasker()
        svc.add_rule(MaskRule("r1", "credit_card", "redact"))
        result = svc.mask({"credit_card": "4111-1111-1111-1111"})
        assert result["data"]["credit_card"] == "[REDACTED]"

    def test_regex_pattern(self):
        svc = DataMasker()
        svc.add_rule(MaskRule("r1", ".*_secret", "full", "***"))
        result = svc.mask({"api_secret": "abc123", "name": "Bob"})
        assert result["data"]["api_secret"] == "***"
        assert result["data"]["name"] == "Bob"

    def test_fields_masked_tracking(self):
        svc = DataMasker()
        svc.add_rule(MaskRule("r1", "password", "full"))
        result = svc.mask({"password": "secret", "id": "1"})
        assert "password" in result["fields_masked"]
        assert "id" not in result["fields_masked"]

    def test_no_rules_passthrough(self):
        svc = DataMasker()
        result = svc.mask({"name": "Alice", "age": "30"})
        assert result["data"]["name"] == "Alice"

    def test_remove_rule(self):
        svc = DataMasker()
        svc.add_rule(MaskRule("r1", "secret", "full"))
        svc.remove_rule("r1")
        result = svc.mask({"secret": "value"})
        assert result["data"]["secret"] == "value"

    def test_stats(self):
        svc = DataMasker()
        svc.add_rule(MaskRule("r1", "pw", "full"))
        svc.mask({"pw": "secret"})
        svc.mask({"pw": "another"})
        stats = svc.get_stats()
        assert stats["total_rules"] == 1
        assert stats["total_masked"] == 2

    def test_invalid_mask_type(self):
        svc = DataMasker()
        with pytest.raises(ValueError):
            svc.add_rule(MaskRule("r1", "x", "encrypt"))

    def test_duplicate_rule(self):
        svc = DataMasker()
        svc.add_rule(MaskRule("r1", "x", "full"))
        with pytest.raises(ValueError):
            svc.add_rule(MaskRule("r1", "y", "full"))

    def test_isolation(self):
        a, b = DataMasker(), DataMasker()
        a.add_rule(MaskRule("r1", "pw", "full"))
        assert b.mask({"pw": "secret"})["data"]["pw"] == "secret"
