"""App environment configuration — sandbox environment variables builder."""


RESERVED_ENV_VARS = frozenset({
    "OPENSKILL_APP_ID", "OPENSKILL_INSTALLATION_ID", "OPENSKILL_ORG_ID",
    "OPENSKILL_FUNCTION", "OPENSKILL_SANDBOX", "PATH", "HOME",
})


def build_sandbox_env(
    *,
    app_id: str,
    installation_id: str,
    org_id: str,
    function_name: str,
    secrets: dict[str, str] | None = None,
    config: dict[str, str] | None = None,
) -> dict[str, str]:
    """Build environment variables for sandbox execution."""
    env = {
        "OPENSKILL_APP_ID": app_id,
        "OPENSKILL_INSTALLATION_ID": installation_id,
        "OPENSKILL_ORG_ID": org_id,
        "OPENSKILL_FUNCTION": function_name,
        "OPENSKILL_SANDBOX": "1",
    }
    # Inject secrets as OPENSKILL_SECRET_<KEY>
    for key, val in (secrets or {}).items():
        env[f"OPENSKILL_SECRET_{key.upper()}"] = val

    # Inject config as OPENSKILL_CONFIG_<KEY>
    for key, val in (config or {}).items():
        env[f"OPENSKILL_CONFIG_{key.upper()}"] = str(val)

    return env


def validate_env_keys(keys: list[str]) -> list[str]:
    """Validate that user-provided env keys don't conflict with reserved ones."""
    conflicts = [k for k in keys if k in RESERVED_ENV_VARS]
    return conflicts
