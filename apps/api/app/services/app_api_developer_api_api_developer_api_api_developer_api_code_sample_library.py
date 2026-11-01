"""App API Developer Code Sample Library — curated code examples by language."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class CodeSample:
    sample_id: str
    title: str
    language: str  # "python", "javascript", "typescript", "go", "ruby", "java", "curl"
    endpoint: str
    code: str
    description: str = ""
    views: int = 0
    copies: int = 0

class AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiCodeSampleLibrary:
    def __init__(self) -> None:
        self._samples: dict[tuple[str, str], CodeSample] = {}

    def add(self, installation_id: str, sample_id: str, title: str, language: str, endpoint: str, code: str, description: str = "") -> CodeSample:
        if not installation_id: raise ValueError("installation_id is required")
        valid_langs = {"python", "javascript", "typescript", "go", "ruby", "java", "curl"}
        if language not in valid_langs: raise ValueError(f"Unsupported language: {language}")
        key = (installation_id, sample_id)
        if key in self._samples: raise ValueError(f"Sample {sample_id} exists")
        s = CodeSample(sample_id=sample_id, title=title, language=language, endpoint=endpoint, code=code, description=description)
        self._samples[key] = s
        return s

    def view(self, installation_id: str, sample_id: str) -> CodeSample:
        s = self._get(installation_id, sample_id)
        s.views += 1
        return s

    def copy(self, installation_id: str, sample_id: str) -> CodeSample:
        s = self._get(installation_id, sample_id)
        s.copies += 1
        return s

    def by_language(self, installation_id: str, language: str) -> list[CodeSample]:
        return [s for (inst, _), s in self._samples.items() if inst == installation_id and s.language == language]

    def by_endpoint(self, installation_id: str, endpoint: str) -> list[CodeSample]:
        return [s for (inst, _), s in self._samples.items() if inst == installation_id and s.endpoint == endpoint]

    def popular(self, installation_id: str, limit: int = 10) -> list[CodeSample]:
        samples = [s for (inst, _), s in self._samples.items() if inst == installation_id]
        return sorted(samples, key=lambda s: s.views + s.copies * 3, reverse=True)[:limit]

    def language_counts(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for (inst, _), s in self._samples.items():
            if inst == installation_id: counts[s.language] = counts.get(s.language, 0) + 1
        return counts

    def _get(self, installation_id: str, sample_id: str) -> CodeSample:
        key = (installation_id, sample_id)
        s = self._samples.get(key)
        if s is None: raise KeyError(f"Sample {sample_id} not found")
        return s
