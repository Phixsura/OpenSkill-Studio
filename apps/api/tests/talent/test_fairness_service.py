"""Fairness service tests — verify structure and constants."""

from app.talent.services.fairness import FairnessService


class TestFairnessServiceExists:
    def test_class_exists(self):
        assert FairnessService is not None

    def test_has_compute_method(self):
        assert hasattr(FairnessService, "compute_fairness_metrics")

    def test_requires_db(self):
        """FairnessService.__init__ requires a db parameter."""
        import inspect
        sig = inspect.signature(FairnessService.__init__)
        params = list(sig.parameters.keys())
        assert "db" in params
