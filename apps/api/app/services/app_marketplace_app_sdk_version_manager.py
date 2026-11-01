"""SDK version manager — track and manage SDK versions across languages."""

SDKS = {
    "typescript": {"package": "@openskill/sdk", "repo": "sdk-typescript"},
    "python": {"package": "openskill-sdk", "repo": "sdk-python"},
    "go": {"package": "github.com/openskill/sdk-go", "repo": "sdk-go"},
    "ruby": {"package": "openskill-sdk", "repo": "sdk-ruby"},
}

def get_sdk_info(*, language: str) -> dict | None:
    return SDKS.get(language)

def check_sdk_compatibility(*, sdk_version: str, api_version: str) -> dict:
    sdk_major = int(sdk_version.split(".")[0]) if sdk_version else 0
    api_major = int(api_version.replace("v", "").split(".")[0]) if api_version else 0
    compatible = sdk_major >= api_major
    return {"compatible": compatible, "sdk_version": sdk_version, "api_version": api_version,
            "recommendation": None if compatible else f"Upgrade SDK to {api_major}.x"}

def list_sdks() -> list[dict]:
    return [{"language": k, **v} for k, v in SDKS.items()]
