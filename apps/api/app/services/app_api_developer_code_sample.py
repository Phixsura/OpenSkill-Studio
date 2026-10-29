"""App API Developer Code Sample — manage API code samples by language."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class CodeSample:
    sample_id: str
    endpoint: str
    language: str
    code: str
    title: str = ""
    copy_count: int = 0

class AppAPIDeveloperCodeSample:
    def __init__(self) -> None:
        self._samples: dict[tuple[str, str], CodeSample] = {}

    def add(self, installation_id: str, sample_id: str, endpoint: str, language: str, code: str, title: str = "") -> CodeSample:
        if not installation_id: raise ValueError("installation_id is required")
        if not code.strip(): raise ValueError("code cannot be empty")
        key = (installation_id, sample_id)
        if key in self._samples: raise ValueError(f"Sample {sample_id} exists")
        s = CodeSample(sample_id=sample_id, endpoint=endpoint, language=language, code=code, title=title)
        self._samples[key] = s
        return s

    def record_copy(self, installation_id: str, sample_id: str) -> CodeSample:
        s = self._samples.get((installation_id, sample_id))
        if s is None: raise KeyError(f"Sample {sample_id} not found")
        s.copy_count += 1
        return s

    def by_endpoint(self, installation_id: str, endpoint: str) -> list[CodeSample]:
        return [s for (inst, _), s in self._samples.items() if inst == installation_id and s.endpoint == endpoint]

    def by_language(self, installation_id: str, language: str) -> list[CodeSample]:
        return [s for (inst, _), s in self._samples.items() if inst == installation_id and s.language == language]

    def list_samples(self, installation_id: str) -> list[CodeSample]:
        return [s for (inst, _), s in self._samples.items() if inst == installation_id]
