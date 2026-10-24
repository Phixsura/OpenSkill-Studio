"""SDK version — SDK download and version management."""

import html

SDKS = {
    "typescript": {"latest": "3.2.0", "min_supported": "2.0.0", "install": "npm install @openskill/sdk"},
    "python": {"latest": "2.1.0", "min_supported": "1.5.0", "install": "pip install openskill-sdk"},
    "go": {"latest": "1.4.0", "min_supported": "1.0.0", "install": "go get github.com/openskill/sdk-go"},
    "ruby": {"latest": "1.2.0", "min_supported": "1.0.0", "install": "gem install openskill-sdk"},
}


def get_sdk_info(*, language: str) -> dict:
    sdk = SDKS.get(language)
    if not sdk:
        return {"error": f"No SDK for: {language}", "available": list(SDKS.keys())}
    return {"language": language, **sdk}


def list_sdks() -> dict:
    items = [{"language": k, **v} for k, v in SDKS.items()]
    return {"sdks": items, "total": len(items)}
