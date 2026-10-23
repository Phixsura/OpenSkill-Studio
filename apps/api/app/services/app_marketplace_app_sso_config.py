"""SSO config — configure single sign-on providers for enterprise apps."""

import re

URL_RE = re.compile(r"^https://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$")


SSO_PROVIDERS = {
    "saml": {"label": "SAML 2.0", "fields": ["metadata_url", "entity_id", "certificate"]},
    "oidc": {"label": "OpenID Connect", "fields": ["issuer_url", "client_id", "client_secret"]},
    "oauth2": {"label": "OAuth 2.0", "fields": ["auth_url", "token_url", "client_id", "client_secret"]},
}


def configure_sso(*, app_id: str, provider: str, config: dict) -> dict:
    if provider not in SSO_PROVIDERS:
        return {"error": f"Unknown provider. Valid: {', '.join(sorted(SSO_PROVIDERS))}"}
    prov = SSO_PROVIDERS[provider]
    missing = [f for f in prov["fields"] if not config.get(f)]
    if missing:
        return {"error": f"Missing required fields: {', '.join(missing)}"}
    # Validate URLs
    for field in prov["fields"]:
        if field.endswith("_url") and not URL_RE.match(config.get(field, "")):
            return {"error": f"Invalid URL for {field}"}
    return {
        "app_id": app_id,
        "provider": provider,
        "provider_label": prov["label"],
        "status": "configured",
        "login_url": f"https://marketplace.openskill.dev/sso/{app_id}/login",
        "callback_url": f"https://marketplace.openskill.dev/sso/{app_id}/callback",
    }


def list_sso_providers() -> dict:
    return {"providers": [{"id": k, **v} for k, v in SSO_PROVIDERS.items()]}
