"""Tests for App Token Exchange — codes, exchange, refresh, revoke."""

import pytest

from app.services.app_token_exchange import AppTokenExchange


class TestIssueCode:
    def test_issue(self):
        e = AppTokenExchange()
        code = e.issue_code("inst-1", "user-1", scopes=["read"], now=1000.0)
        assert len(code.code) > 20
        assert code.scopes == ["read"]

    def test_missing_user(self):
        e = AppTokenExchange()
        with pytest.raises(ValueError):
            e.issue_code("inst-1", "")


class TestExchangeCode:
    def test_exchange(self):
        e = AppTokenExchange()
        code = e.issue_code("inst-1", "user-1", now=1000.0)
        pair = e.exchange_code(code.code, "inst-1", now=1000.0)
        assert len(pair.access_token) > 20
        assert len(pair.refresh_token) > 20
        assert pair.user_id == "user-1"

    def test_wrong_installation(self):
        e = AppTokenExchange()
        code = e.issue_code("inst-1", "user-1", now=1000.0)
        with pytest.raises(PermissionError):
            e.exchange_code(code.code, "inst-2", now=1000.0)

    def test_double_exchange(self):
        e = AppTokenExchange()
        code = e.issue_code("inst-1", "user-1", now=1000.0)
        e.exchange_code(code.code, "inst-1", now=1000.0)
        with pytest.raises(ValueError, match="already exchanged"):
            e.exchange_code(code.code, "inst-1", now=1000.0)

    def test_expired_code(self):
        e = AppTokenExchange(code_ttl_seconds=60)
        code = e.issue_code("inst-1", "user-1", now=1000.0)
        with pytest.raises(ValueError, match="expired"):
            e.exchange_code(code.code, "inst-1", now=1061.0)

    def test_invalid_code(self):
        e = AppTokenExchange()
        with pytest.raises(KeyError):
            e.exchange_code("bogus", "inst-1")


class TestRefresh:
    def test_refresh(self):
        e = AppTokenExchange()
        code = e.issue_code("inst-1", "user-1", now=1000.0)
        pair = e.exchange_code(code.code, "inst-1", now=1000.0)
        new_pair = e.refresh(pair.refresh_token, now=1001.0)
        assert new_pair.access_token != pair.access_token
        assert new_pair.refresh_token != pair.refresh_token

    def test_old_token_revoked(self):
        e = AppTokenExchange()
        code = e.issue_code("inst-1", "user-1", now=1000.0)
        pair = e.exchange_code(code.code, "inst-1", now=1000.0)
        e.refresh(pair.refresh_token, now=1001.0)
        assert e.validate_token(pair.access_token) is None

    def test_invalid_refresh(self):
        e = AppTokenExchange()
        with pytest.raises(KeyError):
            e.refresh("bogus")


class TestValidate:
    def test_valid(self):
        e = AppTokenExchange()
        code = e.issue_code("inst-1", "user-1", now=1000.0)
        pair = e.exchange_code(code.code, "inst-1", now=1000.0)
        result = e.validate_token(pair.access_token, now=1000.0)
        assert result is not None
        assert result.user_id == "user-1"

    def test_expired(self):
        e = AppTokenExchange(access_ttl_seconds=60)
        code = e.issue_code("inst-1", "user-1", now=1000.0)
        pair = e.exchange_code(code.code, "inst-1", now=1000.0)
        assert e.validate_token(pair.access_token, now=1061.0) is None

    def test_revoked(self):
        e = AppTokenExchange()
        code = e.issue_code("inst-1", "user-1", now=1000.0)
        pair = e.exchange_code(code.code, "inst-1", now=1000.0)
        e.revoke_token(pair.access_token)
        assert e.validate_token(pair.access_token) is None
