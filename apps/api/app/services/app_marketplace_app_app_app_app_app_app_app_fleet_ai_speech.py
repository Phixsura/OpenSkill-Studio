"""Fleet AI Speech — track speech-to-text and text-to-speech pipelines."""
from __future__ import annotations
def fleet_ai_speech(services: list[dict]) -> dict:
    active = [s for s in services if s.get("active", True)]
    hours_processed = round(sum(s.get("hours_24h", 0) for s in services), 1)
    languages = set()
    for s in services:
        languages.update(s.get("languages", []))
    wer = round(sum(s.get("wer", 0) for s in services) / max(len(services), 1), 2)
    return {"services": len(services), "active": len(active), "hours_24h": hours_processed,
            "languages": len(languages), "wer": wer, "accurate": wer < 5}
