"""LTI Dynamic Registration 1.0 (R87 — 1EdTech).

The LMS admin pastes two values the platform shows them (its
openid-configuration URL and a one-time registration token); we fetch the
platform's configuration, POST our client registration to its
registration_endpoint, and persist the resulting LtiRegistration — no
copy-pasting of five endpoint URLs + client id by hand.

Trust: both URLs are egress-screened; the platform configuration MUST carry
the lti-platform-configuration claim (refuses plain OIDC servers); the
registration access token is used once and never stored.
"""

from __future__ import annotations

import json

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.exceptions import AppError
from app.integrations.models import LtiRegistration
from app.integrations.security import EgressClient, validate_egress_url
from app.integrations.services.lti import LtiService

log = structlog.get_logger()

PLATFORM_CONFIG_CLAIM = "https://purl.imsglobal.org/spec/lti-platform-configuration"
TOOL_CONFIG_CLAIM = "https://purl.imsglobal.org/spec/lti-tool-configuration"
_REQUIRED_CONFIG_KEYS = (
    "issuer",
    "authorization_endpoint",
    "token_endpoint",
    "jwks_uri",
    "registration_endpoint",
)


def _tool_registration_payload() -> dict:
    base = settings.public_base_url.rstrip("/")
    launch = f"{base}/api/v1/lti/launch"
    return {
        "application_type": "web",
        "response_types": ["id_token"],
        "grant_types": ["client_credentials", "implicit"],
        "initiate_login_uri": f"{base}/api/v1/lti/login",
        "redirect_uris": [launch],
        "client_name": "OpenSkill Studio",
        "jwks_uri": f"{base}/api/v1/lti/jwks",
        "token_endpoint_auth_method": "private_key_jwt",
        "scope": (
            "https://purl.imsglobal.org/spec/lti-ags/scope/score "
            "https://purl.imsglobal.org/spec/lti-nrps/scope/contextmembership.readonly"
        ),
        TOOL_CONFIG_CLAIM: {
            "domain": base.split("://", 1)[-1].split("/", 1)[0],
            "target_link_uri": launch,
            "claims": ["iss", "sub", "name", "email"],
            "messages": [
                {"type": "LtiResourceLinkRequest", "target_link_uri": launch},
                {"type": "LtiDeepLinkingRequest", "target_link_uri": launch},
            ],
        },
    }


async def dynamic_register(
    db: AsyncSession,
    org_id: str,
    *,
    openid_configuration_url: str,
    registration_token: str | None,
    egress: EgressClient | None = None,
) -> LtiRegistration:
    validate_egress_url(openid_configuration_url)
    egress = egress or EgressClient()
    resp = await egress.request("GET", openid_configuration_url)
    if resp.status_code != 200:
        raise AppError(
            "LTI_DYNREG_CONFIG_FAILED", f"platform config {resp.status_code}", 502
        )
    try:
        config = resp.json()
    except Exception as exc:
        raise AppError("LTI_DYNREG_CONFIG_FAILED", "config not JSON", 502) from exc
    missing = [k for k in _REQUIRED_CONFIG_KEYS if not isinstance(config.get(k), str)]
    if missing:
        raise AppError(
            "LTI_DYNREG_CONFIG_INVALID", f"config missing {missing}", 422
        )
    if not isinstance(config.get(PLATFORM_CONFIG_CLAIM), dict):
        raise AppError(
            "LTI_DYNREG_CONFIG_INVALID",
            "not an LTI platform (lti-platform-configuration claim absent)",
            422,
        )
    for key in ("authorization_endpoint", "token_endpoint", "jwks_uri", "registration_endpoint"):
        validate_egress_url(config[key])
    # R253 (R251/R252 class — platform mix-up defense): the issuer must share
    # the ORIGIN of the admin-pasted configuration URL. Strict OIDC-Discovery
    # §4.3 derivation would break real LMSes (Moodle serves its config at a
    # non-standard path), but a cross-origin issuer means the document is
    # registering us against a DIFFERENT platform than the one the admin
    # trusted — refuse it.
    from urllib.parse import urlsplit as _us

    cfg_o, iss_o = _us(openid_configuration_url), _us(config["issuer"])
    if (cfg_o.scheme, cfg_o.netloc) != (iss_o.scheme, iss_o.netloc):
        raise AppError(
            "LTI_DYNREG_CONFIG_INVALID",
            "issuer origin does not match the configuration URL",
            422,
        )

    headers = {"content-type": "application/json", "accept": "application/json"}
    if registration_token:
        headers["authorization"] = f"Bearer {registration_token}"
    reg_resp = await egress.request(
        "POST",
        config["registration_endpoint"],
        headers=headers,
        content=json.dumps(_tool_registration_payload()).encode(),
    )
    if reg_resp.status_code not in (200, 201):
        raise AppError(
            "LTI_DYNREG_REFUSED",
            f"platform refused the registration ({reg_resp.status_code})",
            502,
        )
    try:
        reg = reg_resp.json()
    except Exception as exc:
        raise AppError("LTI_DYNREG_REFUSED", "registration response not JSON", 502) from exc
    client_id = reg.get("client_id")
    if not isinstance(client_id, str) or not client_id:
        raise AppError("LTI_DYNREG_REFUSED", "no client_id in response", 502)
    tool_cfg = reg.get(TOOL_CONFIG_CLAIM) or {}
    deployment_ids = [
        str(d) for d in (tool_cfg.get("deployment_ids") or []) if isinstance(d, str | int)
    ]

    return await LtiService(db).create_registration(
        org_id,
        issuer=config["issuer"],
        client_id=client_id,
        auth_login_url=config["authorization_endpoint"],
        auth_token_url=config["token_endpoint"],
        jwks_url=config["jwks_uri"],
        deployment_ids=deployment_ids,
    )
