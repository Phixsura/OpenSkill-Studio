"""Connection string builder — generate and parse database URIs."""
from __future__ import annotations
from urllib.parse import quote_plus


TEMPLATES = {
    "postgres": "postgresql://{user}:{password}@{host}:{port}/{database}",
    "mysql": "mysql://{user}:{password}@{host}:{port}/{database}",
    "mongodb": "mongodb://{user}:{password}@{host}:{port}/{database}",
    "redis": "redis://:{password}@{host}:{port}/{database}",
}


def build_connection_string(engine: str, host: str, port: int, database: str,
                             user: str = "", password: str = "",
                             params: dict | None = None) -> dict:
    if engine not in TEMPLATES:
        return {"built": False, "error": f"unsupported engine, use {sorted(TEMPLATES)}"}
    safe_user = quote_plus(user)
    safe_pass = quote_plus(password)
    uri = TEMPLATES[engine].format(user=safe_user, password=safe_pass,
                                     host=host, port=port, database=database)
    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        uri += f"?{qs}"
    masked = uri.replace(safe_pass, "****") if safe_pass else uri
    return {"built": True, "uri": uri, "masked": masked, "engine": engine}


def parse_connection_info(uri: str) -> dict:
    for engine, tpl in TEMPLATES.items():
        if uri.startswith(engine.split("://")[0] if "://" in engine else engine):
            return {"engine": engine, "uri_length": len(uri), "has_auth": "@" in uri}
    return {"engine": "unknown", "uri_length": len(uri), "has_auth": "@" in uri}
