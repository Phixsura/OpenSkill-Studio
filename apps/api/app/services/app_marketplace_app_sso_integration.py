"""SSO integration — SAML/OIDC single sign-on for enterprise apps."""

import hashlib
import secrets


def create_sso_config(*, app_id: str, provider: str, client_id: str,
                        issuer_url: str, callback_url: str) -> dict:
    valid_providers = {"saml", "oidc", "google", "azure_ad", "okta"}
    if provider not in valid_providers:
        return {"error": f"Unsupported provider. Use: {', '.join(sorted(valid_providers))}"}
    return {"app_id": app_id, "provider": provider, "client_id": client_id,
            "issuer_url": issuer_url, "callback_url": callback_url,
            "status": "configured", "error": None}


def generate_state_param(*, session_id: str) -> str:
    return hashlib.sha256(f"{session_id}:{secrets.token_hex(16)}".encode()).hexdigest()[:32]


def validate_callback(*, state: str, code: str, expected_state: str) -> dict:
    if state != expected_state:
        return {"valid": False, "error": "State mismatch — possible CSRF"}
    if not code:
        return {"valid": False, "error": "Missing authorization code"}
    return {"valid": True, "error": None}


def build_sso_metadata(*, app: dict, sso_config: dict) -> dict:
    return {"entity_id": f"https://openskill.dev/sso/{app.get('slug', '')}",
            "acs_url": sso_config.get("callback_url"),
            "provider": sso_config.get("provider"), "name_id_format": "email"}
