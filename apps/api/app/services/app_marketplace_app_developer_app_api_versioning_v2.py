"""API versioning v2 — header-based versioning with sunset headers and migration paths."""


def resolve_api_version(*, accept_header: str | None, url_version: str | None,
                           default_version: str = "v1") -> dict:
    if url_version:
        return {"version": url_version, "source": "url"}
    if accept_header:
        # Parse: application/vnd.openskill.v2+json
        import re
        m = re.search(r'vnd\.openskill\.(v\d+)', accept_header)
        if m:
            return {"version": m.group(1), "source": "accept_header"}
    return {"version": default_version, "source": "default"}


def build_version_negotiation_response(*, requested: str, available: list[str],
                                          deprecated: list[str]) -> dict:
    if requested in available:
        headers = {}
        if requested in deprecated:
            headers["Deprecation"] = "true"
            headers["Sunset"] = "2027-01-01"
        return {"status": 200, "version": requested, "headers": headers}
    return {"status": 406, "version": None, "error": f"Version {requested} not available",
            "available": available}


def compute_version_adoption(*, requests_by_version: dict[str, int]) -> list[dict]:
    total = sum(requests_by_version.values())
    return [{"version": v, "requests": c, "pct": round(c / max(total, 1) * 100, 1)}
            for v, c in sorted(requests_by_version.items(), key=lambda x: -x[1])]
