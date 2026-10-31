"""Tests for Consumer API Pagination Helper service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_pagination import PaginationHelper


class TestPaginationHelper:
    def test_offset_basic(self):
        svc = PaginationHelper()
        items = list(range(50))
        result = svc.paginate_offset(items, page=1, page_size=10)
        assert len(result["data"]) == 10
        assert result["meta"]["total_items"] == 50
        assert result["meta"]["total_pages"] == 5
        assert result["meta"]["has_next"] is True

    def test_offset_last_page(self):
        svc = PaginationHelper()
        items = list(range(25))
        result = svc.paginate_offset(items, page=3, page_size=10)
        assert len(result["data"]) == 5
        assert result["meta"]["has_next"] is False
        assert result["meta"]["has_prev"] is True

    def test_offset_page_1_no_prev(self):
        svc = PaginationHelper()
        result = svc.paginate_offset(list(range(10)), page=1, page_size=5)
        assert result["meta"]["has_prev"] is False

    def test_cursor_basic(self):
        svc = PaginationHelper()
        items = list(range(30))
        r1 = svc.paginate_cursor(items, page_size=10)
        assert len(r1["data"]) == 10
        assert r1["meta"]["has_more"] is True
        r2 = svc.paginate_cursor(items, cursor=r1["meta"]["next_cursor"], page_size=10)
        assert r2["data"][0] == 10

    def test_cursor_last_page(self):
        svc = PaginationHelper()
        items = list(range(15))
        r1 = svc.paginate_cursor(items, page_size=10)
        r2 = svc.paginate_cursor(items, cursor=r1["meta"]["next_cursor"], page_size=10)
        assert r2["meta"]["has_more"] is False
        assert r2["meta"]["next_cursor"] is None

    def test_max_page_size_capped(self):
        svc = PaginationHelper()
        svc.configure(default_page_size=10, max_page_size=50)
        result = svc.paginate_offset(list(range(200)), page=1, page_size=100)
        assert result["meta"]["page_size"] == 50

    def test_configure(self):
        svc = PaginationHelper()
        svc.configure(default_page_size=25, max_page_size=200, strategy="cursor")
        config = svc.get_config()
        assert config["strategy"] == "cursor"
        assert config["default_page_size"] == 25

    def test_paginate_auto_offset(self):
        svc = PaginationHelper()
        svc.configure(strategy="offset")
        result = svc.paginate(list(range(20)), page=2, page_size=5)
        assert result["data"][0] == 5

    def test_paginate_auto_cursor(self):
        svc = PaginationHelper()
        svc.configure(strategy="cursor")
        result = svc.paginate(list(range(20)), page_size=5)
        assert len(result["data"]) == 5
        assert result["meta"]["has_more"] is True

    def test_invalid_page(self):
        svc = PaginationHelper()
        with pytest.raises(ValueError):
            svc.paginate_offset([], page=0)

    def test_invalid_cursor(self):
        svc = PaginationHelper()
        with pytest.raises(ValueError):
            svc.paginate_cursor([], cursor="bad-cursor")

    def test_invalid_strategy(self):
        svc = PaginationHelper()
        with pytest.raises(ValueError):
            svc.configure(strategy="graphql")
