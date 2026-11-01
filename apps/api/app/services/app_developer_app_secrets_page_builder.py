"""Secrets page builder — compile secrets management page data."""

def build_secrets_page(*, secrets: list[dict], max_secrets: int = 20) -> dict:
    return {"secrets": secrets, "count": len(secrets), "max": max_secrets,
            "can_add": len(secrets) < max_secrets, "remaining": max_secrets - len(secrets)}
