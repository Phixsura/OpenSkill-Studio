"""Version sorter tests."""
import pytest
from app.services.app_version_sorter import sort_versions, get_latest_version, is_prerelease

def test_sort_desc():
    assert sort_versions(["1.0.0", "2.0.0", "1.5.0"]) == ["2.0.0", "1.5.0", "1.0.0"]

def test_sort_asc():
    assert sort_versions(["2.0.0", "1.0.0"], descending=False) == ["1.0.0", "2.0.0"]

def test_latest():
    assert get_latest_version(["1.0.0", "3.0.0", "2.0.0"]) == "3.0.0"

def test_latest_empty():
    assert get_latest_version([]) is None

def test_prerelease():
    assert is_prerelease("1.0.0-beta") is True
    assert is_prerelease("1.0.0") is False
