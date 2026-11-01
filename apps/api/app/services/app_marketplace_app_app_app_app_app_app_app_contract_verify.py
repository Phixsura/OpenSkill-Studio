"""Service contract verifier — verify service contracts at runtime."""
from __future__ import annotations


def verify_contract(producer: dict, consumer: dict) -> dict:
    producer_fields = set(producer.get("provides", {}).keys())
    consumer_fields = set(consumer.get("requires", {}).keys())
    missing = sorted(consumer_fields - producer_fields)
    type_mismatches = []
    for field in consumer_fields & producer_fields:
        if producer["provides"][field] != consumer["requires"][field]:
            type_mismatches.append({"field": field,
                                     "producer_type": producer["provides"][field],
                                     "consumer_type": consumer["requires"][field]})
    compatible = len(missing) == 0 and len(type_mismatches) == 0
    return {"compatible": compatible, "missing_fields": missing,
            "type_mismatches": type_mismatches,
            "producer": producer.get("name", ""), "consumer": consumer.get("name", "")}


def verify_all_contracts(contracts: list[dict]) -> dict:
    results = []
    for c in contracts:
        r = verify_contract(c["producer"], c["consumer"])
        results.append(r)
    compatible = sum(1 for r in results if r["compatible"])
    return {"total": len(results), "compatible": compatible,
            "incompatible": len(results) - compatible,
            "all_compatible": compatible == len(results)}
