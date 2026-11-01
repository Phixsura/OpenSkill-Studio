import pytest
from app.services.app_api_developer_api_api_ab_test_manager import AppAPIDeveloperAPIApiABTestManager

class TestABTestManager:
    def test_create(self):
        m = AppAPIDeveloperAPIApiABTestManager()
        t = m.create("inst-1", "t1", "/api/checkout", [{"name": "control", "weight": 50}, {"name": "variant_a", "weight": 50}])
        assert len(t.variants) == 2

    def test_need_two_variants(self):
        m = AppAPIDeveloperAPIApiABTestManager()
        with pytest.raises(ValueError):
            m.create("inst-1", "t1", "/api", [{"name": "only", "weight": 100}])

    def test_assign_deterministic(self):
        m = AppAPIDeveloperAPIApiABTestManager()
        m.create("inst-1", "t1", "/api", [{"name": "A", "weight": 50}, {"name": "B", "weight": 50}])
        v1 = m.assign("inst-1", "t1", "user-1")
        v2 = m.assign("inst-1", "t1", "user-1")
        assert v1 == v2

    def test_convert_and_winner(self):
        m = AppAPIDeveloperAPIApiABTestManager()
        m.create("inst-1", "t1", "/api", [{"name": "A", "weight": 50}, {"name": "B", "weight": 50}])
        for i in range(10): m.assign("inst-1", "t1", f"u{i}")
        m.convert("inst-1", "t1", "A")
        m.convert("inst-1", "t1", "A")
        m.convert("inst-1", "t1", "B")
        t = m.complete("inst-1", "t1")
        assert t.winner is not None

    def test_isolation(self):
        m = AppAPIDeveloperAPIApiABTestManager()
        m.create("inst-1", "t1", "/api", [{"name": "A", "weight": 50}, {"name": "B", "weight": 50}])
        assert len(m.list_tests("inst-2")) == 0
