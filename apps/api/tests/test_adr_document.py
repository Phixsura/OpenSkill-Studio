"""Verify ADR-016 developer platform design document exists and has key sections."""

import os
import pytest

ADR_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "docs", "design", "016-developer-platform-sdk.md")

def test_adr_exists():
    assert os.path.isfile(ADR_PATH), f"ADR not found at {ADR_PATH}"

def test_adr_has_content():
    with open(ADR_PATH) as f:
        content = f.read()
    assert len(content) > 1000, "ADR is too short"

EXPECTED_SECTIONS = [
    "Developer Organization",
    "App Model",
    "OAuth",
    "SDK",
    "Sandbox",
    "UI Extension",
    "Event",
    "Manifest",
    "Review",
    "Marketplace",
]

@pytest.mark.parametrize("section", EXPECTED_SECTIONS)
def test_adr_has_section(section):
    with open(ADR_PATH) as f:
        content = f.read()
    assert section.lower() in content.lower(), f"ADR missing section: {section}"
