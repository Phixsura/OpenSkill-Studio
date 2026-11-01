import pytest
from app.services.app_api_developer_api_api_developer_api_api_developer_api_getting_started_wizard import AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiGettingStartedWizard

class TestGettingStartedWizard:
    def test_start(self):
        w = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiGettingStartedWizard()
        p = w.start("inst-1", "dev1")
        assert p.progress_pct == 0.0
        assert p.next_step == "create_account"

    def test_complete_steps(self):
        w = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiGettingStartedWizard()
        w.start("inst-1", "dev1")
        w.complete_step("inst-1", "dev1", "create_account")
        w.complete_step("inst-1", "dev1", "generate_api_key")
        p = w.get_progress("inst-1", "dev1")
        assert p.progress_pct == 40.0
        assert p.next_step == "make_first_call"

    def test_full_completion(self):
        w = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiGettingStartedWizard()
        w.start("inst-1", "dev1")
        for step in ["create_account", "generate_api_key", "make_first_call", "configure_webhook", "go_live"]:
            w.complete_step("inst-1", "dev1", step)
        p = w.get_progress("inst-1", "dev1")
        assert p.is_complete is True
        assert p.completed_at is not None

    def test_completion_rate(self):
        w = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiGettingStartedWizard()
        w.start("inst-1", "d1")
        w.start("inst-1", "d2")
        for step in ["create_account", "generate_api_key", "make_first_call", "configure_webhook", "go_live"]:
            w.complete_step("inst-1", "d1", step)
        assert w.completion_rate("inst-1") == 50.0

    def test_isolation(self):
        w = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiGettingStartedWizard()
        w.start("inst-1", "d1")
        assert w.completion_rate("inst-2") == 0.0
