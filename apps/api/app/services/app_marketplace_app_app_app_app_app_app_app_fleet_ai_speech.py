"""Fleet AI Speech — track speech-to-text and text-to-speech."""
from __future__ import annotations
def fleet_ai_speech(services: list[dict]) -> dict:
    active = [s for s in services if s.get("active", True)]
    stt_hours = sum(s.get("stt_hours_24h", 0) for s in services)
    tts_chars = sum(s.get("tts_chars_24h", 0) for s in services)
    return {"services": len(services), "active": len(active), "stt_hours_24h": stt_hours,
            "tts_chars_24h": tts_chars, "all_active": len(active) == len(services)}
