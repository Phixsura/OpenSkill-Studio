from app.services.app_api_developer_api_api_onboarding_checklist import AppAPIDeveloperAPIApiOnboardingChecklist

class TestOnboardingChecklist:
    def _setup(self):
        c = AppAPIDeveloperAPIApiOnboardingChecklist()
        c.set_template("inst-1", [
            {"item_id": "create_key", "title": "Create API Key"},
            {"item_id": "first_call", "title": "Make First API Call"},
            {"item_id": "webhook", "title": "Set Up Webhook", "required": False},
        ])
        return c

    def test_start(self):
        c = self._setup()
        p = c.start("inst-1", "dev1")
        assert len(p.items) == 3
        assert p.completion_pct == 0.0

    def test_complete(self):
        c = self._setup()
        c.start("inst-1", "dev1")
        c.complete_item("inst-1", "dev1", "create_key")
        p = c.get_progress("inst-1", "dev1")
        assert p.completion_pct == 33.3

    def test_all_required(self):
        c = self._setup()
        c.start("inst-1", "dev1")
        c.complete_item("inst-1", "dev1", "create_key")
        c.complete_item("inst-1", "dev1", "first_call")
        p = c.get_progress("inst-1", "dev1")
        assert p.all_required_done is True

    def test_isolation(self):
        c = self._setup()
        c.start("inst-1", "dev1")
        import pytest
        with pytest.raises(KeyError):
            c.get_progress("inst-2", "dev1")
