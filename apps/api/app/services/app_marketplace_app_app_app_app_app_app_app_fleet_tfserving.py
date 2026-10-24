"""Fleet TF Serving — track TensorFlow model serving."""
from __future__ import annotations
def fleet_tfserving_status(instances: list[dict]) -> dict:
    serving = [i for i in instances if i.get("serving", True)]
    models = sum(i.get("models", 0) for i in instances)
    batches_per_sec = sum(i.get("batches_per_sec", 0) for i in instances)
    return {"instances": len(instances), "serving": len(serving), "models": models,
            "batches_per_sec": batches_per_sec, "all_serving": len(serving) == len(instances)}
