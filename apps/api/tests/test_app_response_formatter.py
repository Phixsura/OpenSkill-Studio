"""Response formatter tests."""
import pytest
from app.services.app_response_formatter import data_response, list_response, error_response

def test_data_response():
    r = data_response({"id": "1", "name": "Test"})
    assert r["data"]["id"] == "1"

def test_list_response():
    r = list_response([1, 2, 3], total=10, page=1, per_page=3)
    assert len(r["data"]) == 3
    assert r["meta"]["total"] == 10
    assert r["meta"]["total_pages"] == 4

def test_list_response_single_page():
    r = list_response([1], total=1, page=1, per_page=20)
    assert r["meta"]["total_pages"] == 1

def test_error_response():
    r = error_response("NOT_FOUND", "Not found", status=404)
    assert r["error"]["code"] == "NOT_FOUND"
    assert r["error"]["message"] == "Not found"

def test_error_with_details():
    r = error_response("VALIDATION", "Invalid", details=[{"field": "name"}])
    assert r["error"]["details"][0]["field"] == "name"

def test_error_no_details():
    r = error_response("ERR", "msg")
    assert "details" not in r["error"]
