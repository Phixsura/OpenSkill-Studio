"""Tests for App Data Transformer — rename, map, filter, compute, default."""

import pytest

from app.services.app_data_transformer import AppDataTransformer, TransformRule


class TestDefineRuleset:
    def test_define(self):
        t = AppDataTransformer()
        rules = [TransformRule(rule_id="r1", rule_type="rename", source_field="name", target_field="full_name")]
        result = t.define_ruleset("inst-1", "rs1", rules)
        assert len(result) == 1

    def test_empty_rules(self):
        t = AppDataTransformer()
        with pytest.raises(ValueError, match="at least one"):
            t.define_ruleset("inst-1", "rs1", [])


class TestRename:
    def test_rename_field(self):
        t = AppDataTransformer()
        t.define_ruleset("inst-1", "rs1", [
            TransformRule(rule_id="r1", rule_type="rename", source_field="name", target_field="full_name"),
        ])
        result = t.transform("inst-1", "rs1", {"name": "Alice", "age": 30})
        assert result == {"full_name": "Alice", "age": 30}

    def test_rename_missing_field(self):
        t = AppDataTransformer()
        t.define_ruleset("inst-1", "rs1", [
            TransformRule(rule_id="r1", rule_type="rename", source_field="missing", target_field="x"),
        ])
        result = t.transform("inst-1", "rs1", {"name": "Alice"})
        assert result == {"name": "Alice"}


class TestMapValue:
    def test_map(self):
        t = AppDataTransformer()
        t.define_ruleset("inst-1", "rs1", [
            TransformRule(rule_id="r1", rule_type="map_value", source_field="status",
                          mapping={"0": "inactive", "1": "active"}),
        ])
        result = t.transform("inst-1", "rs1", {"status": "1"})
        assert result["status"] == "active"

    def test_unmapped_value_kept(self):
        t = AppDataTransformer()
        t.define_ruleset("inst-1", "rs1", [
            TransformRule(rule_id="r1", rule_type="map_value", source_field="status",
                          mapping={"0": "inactive"}),
        ])
        result = t.transform("inst-1", "rs1", {"status": "unknown"})
        assert result["status"] == "unknown"


class TestFilter:
    def test_remove_field(self):
        t = AppDataTransformer()
        t.define_ruleset("inst-1", "rs1", [
            TransformRule(rule_id="r1", rule_type="filter", source_field="password"),
        ])
        result = t.transform("inst-1", "rs1", {"name": "Alice", "password": "secret"})
        assert "password" not in result
        assert result["name"] == "Alice"


class TestDefault:
    def test_set_default(self):
        t = AppDataTransformer()
        t.define_ruleset("inst-1", "rs1", [
            TransformRule(rule_id="r1", rule_type="default", source_field="role", default_value="member"),
        ])
        result = t.transform("inst-1", "rs1", {"name": "Alice"})
        assert result["role"] == "member"

    def test_existing_value_kept(self):
        t = AppDataTransformer()
        t.define_ruleset("inst-1", "rs1", [
            TransformRule(rule_id="r1", rule_type="default", source_field="role", default_value="member"),
        ])
        result = t.transform("inst-1", "rs1", {"role": "admin"})
        assert result["role"] == "admin"


class TestCompute:
    def test_concat(self):
        t = AppDataTransformer()
        t.define_ruleset("inst-1", "rs1", [
            TransformRule(rule_id="r1", rule_type="compute", source_field="",
                          target_field="full_name", expression="first + last"),
        ])
        result = t.transform("inst-1", "rs1", {"first": "Alice", "last": "Smith"})
        assert result["full_name"] == "Alice Smith"


class TestBatch:
    def test_batch(self):
        t = AppDataTransformer()
        t.define_ruleset("inst-1", "rs1", [
            TransformRule(rule_id="r1", rule_type="rename", source_field="n", target_field="name"),
        ])
        results = t.transform_batch("inst-1", "rs1", [{"n": "A"}, {"n": "B"}])
        assert results == [{"name": "A"}, {"name": "B"}]


class TestChaining:
    def test_multiple_rules(self):
        t = AppDataTransformer()
        t.define_ruleset("inst-1", "rs1", [
            TransformRule(rule_id="r1", rule_type="rename", source_field="n", target_field="name"),
            TransformRule(rule_id="r2", rule_type="filter", source_field="secret"),
            TransformRule(rule_id="r3", rule_type="default", source_field="role", default_value="user"),
        ])
        result = t.transform("inst-1", "rs1", {"n": "Alice", "secret": "x"})
        assert result == {"name": "Alice", "role": "user"}


class TestIsolation:
    def test_cross_installation(self):
        t = AppDataTransformer()
        t.define_ruleset("inst-1", "rs1", [
            TransformRule(rule_id="r1", rule_type="rename", source_field="a", target_field="b"),
        ])
        with pytest.raises(KeyError):
            t.transform("inst-2", "rs1", {"a": 1})
