"""Environment config — environment variable configuration builder."""
import html
def build_env_config(*, env_vars: dict[str, str], secrets: list[str]) -> dict:
    items = [{"key": k, "value": html.escape(v) if k not in secrets else "••••••",
              "secret": k in secrets} for k, v in env_vars.items()]
    return {"variables": items, "total": len(items), "secret_count": len([i for i in items if i["secret"]])}
