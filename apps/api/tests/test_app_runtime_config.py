"""Runtime config tests."""
import pytest
from app.services.app_runtime_config import get_runtime_config, list_runtimes, is_supported_runtime

def test_python312():
    c = get_runtime_config("python3.12")
    assert c is not None
    assert c["entrypoint"] == "python"

def test_nodejs20():
    c = get_runtime_config("nodejs20")
    assert c["entrypoint"] == "node"

def test_unknown():
    assert get_runtime_config("ruby3.2") is None

def test_list():
    r = list_runtimes()
    assert "python3.12" in r
    assert "nodejs20" in r

def test_is_supported():
    assert is_supported_runtime("python3.12") is True
    assert is_supported_runtime("rust") is False
