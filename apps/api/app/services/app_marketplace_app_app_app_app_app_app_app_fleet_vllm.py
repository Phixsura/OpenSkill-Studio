"""Fleet vLLM — track high-throughput LLM inference."""
from __future__ import annotations
def fleet_vllm_status(instances: list[dict]) -> dict:
    running = [i for i in instances if i.get("running", True)]
    total_tps = sum(i.get("tokens_per_sec", 0) for i in instances)
    gpus = sum(i.get("gpus", 0) for i in instances)
    return {"instances": len(instances), "running": len(running), "tokens_per_sec": total_tps,
            "gpus": gpus, "all_running": len(running) == len(instances)}
