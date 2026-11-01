"""API playground v3 — interactive API testing with saved collections and environments."""


def create_collection(*, name: str, requests: list[dict]) -> dict:
    return {"name": name, "requests": requests, "request_count": len(requests), "shared": False}


def create_environment(*, name: str, variables: dict[str, str]) -> dict:
    return {"name": name, "variables": variables, "variable_count": len(variables)}


def interpolate_request(*, url: str, headers: dict, body: str | None,
                           env: dict[str, str]) -> dict:
    result_url = url
    result_headers = dict(headers)
    result_body = body
    for key, value in env.items():
        placeholder = "{{" + key + "}}"
        result_url = result_url.replace(placeholder, value)
        for hk, hv in result_headers.items():
            result_headers[hk] = hv.replace(placeholder, value)
        if result_body:
            result_body = result_body.replace(placeholder, value)
    return {"url": result_url, "headers": result_headers, "body": result_body}
