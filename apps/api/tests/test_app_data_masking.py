"""Tests for App Data Masking — strategies, batch, rules."""

import pytest

from app.services.app_data_masking import AppDataMasking, MaskRule


class TestDefineRules:
    def test_define(self):
        m = AppDataMasking()
        rules = m.define_rules("inst-1", "rs1", [
            MaskRule(field="email", strategy="partial"),
            MaskRule(field="ssn", strategy="full"),
        ])
        assert len(rules) == 2

    def test_invalid_strategy(self):
        m = AppDataMasking()
        with pytest.raises(ValueError, match="Invalid strategy"):
            m.define_rules("inst-1", "rs1", [MaskRule(field="x", strategy="nope")])


class TestMasking:
    def test_full_mask(self):
        m = AppDataMasking()
        m.define_rules("inst-1", "rs1", [MaskRule(field="password", strategy="full")])
        result = m.apply_mask("inst-1", "rs1", {"password": "secret123", "name": "Alice"})
        assert result["password"] == "***"
        assert result["name"] == "Alice"

    def test_partial_mask(self):
        m = AppDataMasking()
        m.define_rules("inst-1", "rs1", [MaskRule(field="email", strategy="partial", visible_chars=4)])
        result = m.apply_mask("inst-1", "rs1", {"email": "alice@example.com"})
        assert result["email"] == "alic***"

    def test_partial_short_value(self):
        m = AppDataMasking()
        m.define_rules("inst-1", "rs1", [MaskRule(field="code", strategy="partial", visible_chars=10)])
        result = m.apply_mask("inst-1", "rs1", {"code": "abc"})
        assert result["code"] == "***"

    def test_hash_mask(self):
        m = AppDataMasking()
        m.define_rules("inst-1", "rs1", [MaskRule(field="ssn", strategy="hash")])
        result = m.apply_mask("inst-1", "rs1", {"ssn": "123-45-6789"})
        assert result["ssn"] != "123-45-6789"
        assert len(result["ssn"]) == 12

    def test_redact_mask(self):
        m = AppDataMasking()
        m.define_rules("inst-1", "rs1", [MaskRule(field="notes", strategy="redact")])
        result = m.apply_mask("inst-1", "rs1", {"notes": "sensitive info"})
        assert result["notes"] == "[REDACTED]"

    def test_missing_field_unchanged(self):
        m = AppDataMasking()
        m.define_rules("inst-1", "rs1", [MaskRule(field="secret", strategy="full")])
        result = m.apply_mask("inst-1", "rs1", {"name": "Alice"})
        assert result == {"name": "Alice"}


class TestBatch:
    def test_batch(self):
        m = AppDataMasking()
        m.define_rules("inst-1", "rs1", [MaskRule(field="email", strategy="partial")])
        results = m.apply_mask_batch("inst-1", "rs1", [
            {"email": "alice@example.com"},
            {"email": "bob@example.com"},
        ])
        assert all("***" in r["email"] for r in results)


class TestIsolation:
    def test_cross_installation(self):
        m = AppDataMasking()
        m.define_rules("inst-1", "rs1", [MaskRule(field="x", strategy="full")])
        with pytest.raises(KeyError):
            m.apply_mask("inst-2", "rs1", {"x": "val"})
