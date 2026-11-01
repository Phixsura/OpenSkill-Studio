"""Fleet API Data Validation v9 — track response data quality validation."""
from __future__ import annotations
def fleet_api_data_validation_v9(validators: list[dict]) -> dict:
    active = [v for v in validators if v.get("active")]
    anomalies = sum(v.get("anomalies_detected", 0) for v in validators)
    records = sum(v.get("records_validated", 0) for v in validators)
    return {"validators": len(validators), "active": len(active), "anomalies": anomalies,
            "records_validated": records, "healthy": anomalies == 0}
