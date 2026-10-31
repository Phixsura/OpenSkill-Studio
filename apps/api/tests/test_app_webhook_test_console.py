"""Tests for App Webhook Test Console — templates, simulation, history, pass rate."""

import pytest

from app.services.app_webhook_test_console import (
    AppWebhookTestConsole,
    TestStatus,
    WebhookTestRequest,
)


def _req(event_type: str = "skill_pack.published") -> WebhookTestRequest:
    return WebhookTestRequest(
        event_type=event_type,
        payload={"pack_id": "test-123", "name": "Test Pack"},
        webhook_url="https://myapp.example.com/webhook",
        secret="whsec_test",
    )


class TestTemplates:
    def test_get_templates(self):
        console = AppWebhookTestConsole()
        templates = console.get_templates()
        assert "skill_pack.published" in templates
        assert "app.installed" in templates
        assert "submission.graded" in templates

    def test_get_single_template(self):
        console = AppWebhookTestConsole()
        t = console.get_template("skill_pack.published")
        assert t is not None
        assert "pack_id" in t

    def test_unknown_template(self):
        console = AppWebhookTestConsole()
        assert console.get_template("nonexistent.event") is None


class TestSimulation:
    def test_simulate_success(self):
        console = AppWebhookTestConsole()
        result = console.simulate("app-1", _req(), status_code=200, latency_ms=45.0,
                                   response_body='{"ok": true}')
        assert result.status == TestStatus.PASS
        assert result.is_success is True
        assert result.status_code == 200
        assert result.latency_ms == 45.0

    def test_simulate_failure(self):
        console = AppWebhookTestConsole()
        result = console.simulate("app-1", _req(), status_code=500, latency_ms=120.0)
        assert result.status == TestStatus.FAIL
        assert result.is_success is False

    def test_simulate_error(self):
        console = AppWebhookTestConsole()
        result = console.simulate("app-1", _req(), error="Connection refused")
        assert result.status == TestStatus.ERROR
        assert result.error == "Connection refused"

    def test_simulate_pending(self):
        console = AppWebhookTestConsole()
        result = console.simulate("app-1", _req())
        assert result.status == TestStatus.PENDING

    def test_payload_stored(self):
        console = AppWebhookTestConsole()
        result = console.simulate("app-1", _req(), status_code=200)
        assert result.payload_sent["pack_id"] == "test-123"

    def test_auto_id(self):
        console = AppWebhookTestConsole()
        r1 = console.simulate("app-1", _req(), status_code=200)
        r2 = console.simulate("app-1", _req(), status_code=200)
        assert r1.test_id != r2.test_id

    def test_201_is_pass(self):
        console = AppWebhookTestConsole()
        result = console.simulate("app-1", _req(), status_code=201)
        assert result.status == TestStatus.PASS

    def test_204_is_pass(self):
        console = AppWebhookTestConsole()
        result = console.simulate("app-1", _req(), status_code=204)
        assert result.status == TestStatus.PASS


class TestHistory:
    def test_history_stored(self):
        console = AppWebhookTestConsole()
        console.simulate("app-1", _req(), status_code=200)
        console.simulate("app-1", _req(), status_code=500)
        history = console.get_history("app-1")
        assert len(history) == 2

    def test_newest_first(self):
        console = AppWebhookTestConsole()
        console.simulate("app-1", _req("a.event"), status_code=200)
        console.simulate("app-1", _req("b.event"), status_code=200)
        history = console.get_history("app-1")
        assert history[0].event_type == "b.event"

    def test_history_limit(self):
        console = AppWebhookTestConsole()
        for i in range(10):
            console.simulate("app-1", _req(), status_code=200)
        assert len(console.get_history("app-1", limit=3)) == 3

    def test_get_result_by_id(self):
        console = AppWebhookTestConsole()
        r = console.simulate("app-1", _req(), status_code=200)
        found = console.get_result("app-1", r.test_id)
        assert found is not None
        assert found.test_id == r.test_id

    def test_get_result_nonexistent(self):
        console = AppWebhookTestConsole()
        assert console.get_result("app-1", "fake-id") is None

    def test_per_app_isolation(self):
        console = AppWebhookTestConsole()
        console.simulate("app-1", _req(), status_code=200)
        console.simulate("app-2", _req(), status_code=200)
        assert len(console.get_history("app-1")) == 1
        assert len(console.get_history("app-2")) == 1

    def test_clear_history(self):
        console = AppWebhookTestConsole()
        console.simulate("app-1", _req(), status_code=200)
        console.simulate("app-1", _req(), status_code=200)
        count = console.clear_history("app-1")
        assert count == 2
        assert len(console.get_history("app-1")) == 0


class TestPassRate:
    def test_pass_rate(self):
        console = AppWebhookTestConsole()
        console.simulate("app-1", _req(), status_code=200)
        console.simulate("app-1", _req(), status_code=200)
        console.simulate("app-1", _req(), status_code=500)
        assert console.get_pass_rate("app-1") == pytest.approx(66.7, abs=0.1)

    def test_empty_pass_rate(self):
        console = AppWebhookTestConsole()
        assert console.get_pass_rate("app-x") == 0.0

    def test_perfect_pass_rate(self):
        console = AppWebhookTestConsole()
        for _ in range(5):
            console.simulate("app-1", _req(), status_code=200)
        assert console.get_pass_rate("app-1") == 100.0
