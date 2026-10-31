"""App name validator tests."""
import pytest
from app.services.app_name_validator import validate_app_name

VALID = ["My Cool App", "LMS Connector v2", "Analytics Dashboard", "AB"]

@pytest.mark.parametrize("name", VALID)
def test_valid(name):
    assert validate_app_name(name) == []

def test_too_short():
    assert len(validate_app_name("A")) > 0

def test_too_long():
    assert len(validate_app_name("x" * 101)) > 0

def test_reserved():
    assert len(validate_app_name("OpenSkill")) > 0

def test_profanity():
    assert len(validate_app_name("My Fucking App")) > 0
