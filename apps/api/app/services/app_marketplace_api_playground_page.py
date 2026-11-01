"""API playground page — interactive API testing with collections and environments."""


def build_api_playground_page(*, collections: list[dict], environments: list[dict],
                                   recent_requests: list[dict]) -> dict:
    return {
        "page_type": "api_playground",
        "collections": collections,
        "environments": environments,
        "recent_requests": recent_requests[:20],
        "stats": {"collections": len(collections), "environments": len(environments),
                   "total_requests": len(recent_requests)},
        "features": ["request_builder", "response_viewer", "history", "collections",
                       "environments", "code_generation", "export"],
    }


def build_request(*, method: str, url: str, headers: dict, body: str | None,
                     env: dict) -> dict:
    resolved_url = url
    resolved_headers = dict(headers)
    for key, value in env.items():
        placeholder = "{{" + key + "}}"
        resolved_url = resolved_url.replace(placeholder, str(value))
        for hk, hv in resolved_headers.items():
            resolved_headers[hk] = hv.replace(placeholder, str(value))
    return {"method": method.upper(), "url": resolved_url, "headers": resolved_headers,
            "body": body, "ready": True}
