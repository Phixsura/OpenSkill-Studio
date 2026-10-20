"""R530: CrossHair symbolic contracts over the fabric's pure logic cores.

The R206 discipline applied to issue #43: the SMT solver PROVES each
post-condition for ALL inputs in the pre-domain (or emits a concrete
counterexample) — stronger than the 150-sample Hypothesis properties for
the integer/boolean/string-shape logic below.

Run (not part of pytest; CI-nightly class):
    cd apps/api
    uv run --with crosshair-tool crosshair check tests/symbolic/test_fabric_contracts.py --per_condition_timeout=25
"""

from app.integrations.services.model_schema import _format_ok, validate_model_payload


def email_format_requires_both_halves(local: str, domain: str) -> bool:
    """The email format rule accepts exactly one '@' with non-empty halves.

    pre: "@" not in local and "@" not in domain
    post: __return__ == (len(local) > 0 and len(domain) > 0)
    """
    return _format_ok("email", f"{local}@{domain}")


def email_format_rejects_multi_at(value: str) -> bool:
    """More than one '@' (or none) never validates.

    pre: value.count("@") != 1
    post: __return__ is False
    """
    return _format_ok("email", value)


def validator_output_is_bounded(payload: dict) -> int:
    """The walker returns at most 10 violations for ANY payload shape
    (the R494 bound, proven rather than sampled).

    post: 0 <= __return__ <= 10
    """
    return len(validate_model_payload("roster.user", payload))


def validator_none_equals_absent(value: str) -> bool:
    """A None field and an absent field validate identically (the documented
    optionality rule) for every string value of the OTHER field.

    post: __return__ is True
    """
    with_none = validate_model_payload("roster.user", {"email": value, "display_name": None})
    absent = validate_model_payload("roster.user", {"email": value})
    return with_none == absent


def scim_projection_preserves_core(keys: list, attributes: str) -> bool:
    """_project never drops id/schemas whatever the attribute selection.

    pre: all(isinstance(k, str) for k in keys) and len(keys) <= 5
    post: __return__ is True
    """
    from app.integrations.api.scim import _project

    body = dict.fromkeys(keys, "v")
    body["id"] = "ID"
    body["schemas"] = ["urn:x"]
    out = _project(body, attributes or None, None)
    return out.get("id") == "ID" and out.get("schemas") == ["urn:x"]


def export_drop_universe_rule(allow_a: bool, allow_b: bool, drop_a: bool, drop_b: bool) -> bool:
    """_check_exported_columns raises IFF every allowed field is dropped
    (the R502 rule as a boolean identity over a 2-field universe).

    post: __return__ is True
    """
    from app.exceptions import AppError
    from app.integrations.services.warehouse import _check_exported_columns

    allowlist = [f for f, on in (("a", allow_a), ("b", allow_b)) if on]
    anonymize = {f: "drop" for f, on in (("a", drop_a), ("b", drop_b)) if on}
    try:
        _check_exported_columns(allowlist, anonymize)
        raised = False
    except AppError:
        raised = True
    exported = [f for f in allowlist if anonymize.get(f) != "drop"]
    return raised == (len(exported) == 0)


def signature_shape_and_determinism(secret: str, message_id: str, timestamp: int) -> bool:
    """Standard-Webhooks signature: always 'v1,'-prefixed 44-char-b64 of a
    32-byte HMAC, and deterministic for identical inputs.

    pre: len(secret) <= 64 and len(message_id) <= 26 and 0 <= timestamp <= 2**31
    post: __return__ is True
    """
    from app.integrations.services.events import sign_payload

    a = sign_payload(secret, message_id, timestamp, b"{}")
    b = sign_payload(secret, message_id, timestamp, b"{}")
    return a == b and a.startswith("v1,") and len(a) == 3 + 44


def signature_binds_every_input(secret: str, message_id: str, timestamp: int) -> bool:
    """Flipping ANY of secret, id, timestamp or body changes the signature
    (second-preimage sanity over the signed-string construction).

    pre: len(secret) <= 32 and len(message_id) <= 20 and 0 <= timestamp < 2**31 - 1
    post: __return__ is True
    """
    from app.integrations.services.events import sign_payload

    base = sign_payload(secret, message_id, timestamp, b"x")
    return (
        base != sign_payload(secret + "A", message_id, timestamp, b"x")
        and base != sign_payload(secret, message_id + "A", timestamp, b"x")
        and base != sign_payload(secret, message_id, timestamp + 1, b"x")
        and base != sign_payload(secret, message_id, timestamp, b"y")
    )


def sanitize_cell_never_formula_leading(value: str) -> bool:
    """CSV-injection guard: the OUTPUT never starts with a formula trigger,
    and non-formula inputs pass through untouched (S8.3, proven for all
    strings rather than the sampled matrix).

    post: __return__ is True
    """
    from app.integrations.services.bulk_import import _sanitize_cell

    out = _sanitize_cell(value)
    safe = not out or out[0] not in ("=", "+", "-", "@", "\t")
    untouched = (not value or value[0] not in ("=", "+", "-", "@", "\t")) <= (out == value)
    return safe and untouched


def email_domain_normalization_is_idempotent(local: str, domain: str) -> bool:
    """normalized_email_domain is idempotent: re-normalizing its output
    (as a domain of a synthetic address) yields itself — the property the
    R319 claim/compare split depends on.

    pre: "@" not in local and "@" not in domain and len(domain) <= 30
    post: __return__ is True
    """
    from app.integrations.services.domains import normalized_email_domain

    once = normalized_email_domain(f"{local}@{domain}")
    if once == "":
        return True
    twice = normalized_email_domain(f"x@{once}")
    return twice == once


def coerce_active_string_domain(value: str, wrap: bool) -> bool:
    """_coerce_active over ALL strings (and the dict-wrapped Entra form):
    returns a bool exactly for case/space-insensitive "true"/"false",
    None otherwise — total, never raises. (An `object` domain crashes the
    CrossHair proxy machinery on this import graph; bool/dict arms are
    further covered by the DB suites.)

    post: __return__ is True
    """
    from app.integrations.services.scim import _coerce_active

    arg = {"active": value} if wrap else value
    out = _coerce_active(arg)
    low = value.strip().lower()
    if low in ("true", "false"):
        return out == (low == "true")
    return out is None
