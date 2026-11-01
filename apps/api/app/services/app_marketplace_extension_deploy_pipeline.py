"""Extension Deployment Pipeline — CI/CD pipeline for extension releases."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class PipelineStage:
    name: str
    status: str = "pending"  # pending, running, passed, failed, skipped
    duration_ms: float = 0.0
    output: str = ""


@dataclass
class DeployPipeline:
    pipeline_id: str
    extension_id: str
    version: str
    trigger: str = "push"  # push, manual, schedule
    stages: list[PipelineStage] = field(default_factory=list)
    status: str = "pending"  # pending, running, passed, failed
    started_at: float = 0.0
    completed_at: float = 0.0
    def __post_init__(self):
        if not self.started_at: self.started_at = time.time()


class ExtDeployPipelineService:
    DEFAULT_STAGES = ["lint", "test", "build", "security-scan", "deploy"]

    def __init__(self):
        self._pipelines: dict[str, DeployPipeline] = {}
        self._counter = 0

    def create(self, extension_id: str, version: str, trigger: str = "push",
               stages: list[str] | None = None) -> DeployPipeline:
        self._counter += 1
        stage_list = [PipelineStage(name=s) for s in (stages or self.DEFAULT_STAGES)]
        p = DeployPipeline(pipeline_id=f"pipe-{self._counter}",
                           extension_id=extension_id, version=version,
                           trigger=trigger, stages=stage_list)
        self._pipelines[p.pipeline_id] = p
        return p

    def run_stage(self, pipeline_id: str, stage_name: str,
                  passed: bool = True, output: str = "") -> bool:
        p = self._pipelines.get(pipeline_id)
        if not p or p.status == "failed": return False
        if p.status == "pending":
            p.status = "running"
        for stage in p.stages:
            if stage.name == stage_name:
                stage.status = "passed" if passed else "failed"
                stage.output = output
                if not passed:
                    p.status = "failed"
                    # Skip remaining stages
                    for s in p.stages:
                        if s.status == "pending":
                            s.status = "skipped"
                elif all(s.status == "passed" for s in p.stages):
                    p.status = "passed"
                    p.completed_at = time.time()
                return True
        return False

    def get_pipeline(self, pipeline_id: str) -> DeployPipeline | None:
        return self._pipelines.get(pipeline_id)

    def get_by_extension(self, extension_id: str, limit: int = 10) -> list[DeployPipeline]:
        return sorted([p for p in self._pipelines.values()
                       if p.extension_id == extension_id],
                      key=lambda p: p.started_at, reverse=True)[:limit]
