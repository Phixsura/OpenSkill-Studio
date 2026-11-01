"""Consumer API Request Size Analyzer — analyze request/response payload sizes."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class SizeRecord:
    endpoint_path: str
    method: str
    request_bytes: int
    response_bytes: int

@dataclass
class SizeAnalysis:
    endpoint_path: str
    sample_count: int
    avg_request_bytes: int
    avg_response_bytes: int
    max_request_bytes: int
    max_response_bytes: int
    total_transfer_bytes: int

@dataclass
class PlatformSizeStats:
    total_endpoints: int
    total_transfer_gb: float
    largest_endpoint: str
    avg_response_bytes: int

class AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiApiConsumerRequestSizeAnalyzer:
    def __init__(self) -> None:
        self._records: dict[tuple[str, str], list[SizeRecord]] = {}

    def record(self, installation_id: str, record: SizeRecord) -> SizeRecord:
        if not installation_id:
            raise ValueError("installation_id is required")
        if record.request_bytes < 0 or record.response_bytes < 0:
            raise ValueError("Sizes must be non-negative")
        key = (installation_id, record.endpoint_path)
        if key not in self._records:
            self._records[key] = []
        self._records[key].append(record)
        if len(self._records[key]) > 10000:
            self._records[key] = self._records[key][-10000:]
        return record

    def analyze_endpoint(self, installation_id: str, endpoint_path: str) -> SizeAnalysis:
        records = self._records.get((installation_id, endpoint_path), [])
        if not records:
            return SizeAnalysis(endpoint_path=endpoint_path, sample_count=0, avg_request_bytes=0, avg_response_bytes=0, max_request_bytes=0, max_response_bytes=0, total_transfer_bytes=0)
        req_sizes = [r.request_bytes for r in records]
        resp_sizes = [r.response_bytes for r in records]
        total = sum(req_sizes) + sum(resp_sizes)
        return SizeAnalysis(endpoint_path=endpoint_path, sample_count=len(records), avg_request_bytes=sum(req_sizes) // len(records), avg_response_bytes=sum(resp_sizes) // len(records), max_request_bytes=max(req_sizes), max_response_bytes=max(resp_sizes), total_transfer_bytes=total)

    def get_platform_stats(self, installation_id: str) -> PlatformSizeStats:
        endpoints = {ep for (inst, ep) in self._records if inst == installation_id}
        if not endpoints:
            return PlatformSizeStats(total_endpoints=0, total_transfer_gb=0, largest_endpoint="", avg_response_bytes=0)
        analyses = [self.analyze_endpoint(installation_id, ep) for ep in endpoints]
        total_bytes = sum(a.total_transfer_bytes for a in analyses)
        largest = max(analyses, key=lambda a: a.total_transfer_bytes)
        all_resp = sum(a.avg_response_bytes * a.sample_count for a in analyses)
        total_samples = sum(a.sample_count for a in analyses)
        return PlatformSizeStats(total_endpoints=len(endpoints), total_transfer_gb=round(total_bytes / (1024**3), 3), largest_endpoint=largest.endpoint_path, avg_response_bytes=all_resp // max(total_samples, 1))

    def list_endpoints(self, installation_id: str) -> list[str]:
        return sorted({ep for (inst, ep) in self._records if inst == installation_id})
