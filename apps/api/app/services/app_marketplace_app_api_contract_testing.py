"""API contract testing — verify API responses match declared schemas."""


def validate_response_against_contract(*, response: dict, contract: dict) -> dict:
    errors = []
    expected_status = contract.get("status_code", 200)
    if response.get("status_code") != expected_status:
        errors.append(f"Status {response.get('status_code')} != expected {expected_status}")
    required_fields = contract.get("required_fields", [])
    body = response.get("body", {})
    for field in required_fields:
        if field not in body:
            errors.append(f"Missing required field: {field}")
    for field, expected_type in contract.get("field_types", {}).items():
        if field in body:
            actual = type(body[field]).__name__
            if actual != expected_type:
                errors.append(f"Field '{field}': expected {expected_type}, got {actual}")
    return {"valid": len(errors) == 0, "errors": errors}


def run_contract_suite(*, contracts: list[dict], responses: list[dict]) -> dict:
    results = []
    for contract, response in zip(contracts, responses):
        r = validate_response_against_contract(response=response, contract=contract)
        results.append({"endpoint": contract.get("endpoint"), **r})
    passed = sum(1 for r in results if r["valid"])
    return {"total": len(results), "passed": passed, "failed": len(results) - passed,
            "pass_rate": round(passed / max(len(results), 1) * 100, 1), "results": results}
