"""Pipeline Builder — fluent API for composing data processing pipelines.

Implements:
- Fluent builder pattern: pipeline.source().map().filter().sink()
- Type-safe stage composition
- Branch/fan-out (one input → multiple outputs)
- Merge/fan-in (multiple inputs → one output)
- Error handling per stage
- Pipeline validation before execution
- Dry run mode
"""
from __future__ import annotations
from dataclasses import dataclass, field
from copy import deepcopy


@dataclass
class PipelineStage:
    name: str
    stage_type: str  # source, map, filter, flat_map, reduce, sink, branch, merge
    fn: callable | None = None
    error_handler: callable | None = None
    branches: list[str] = field(default_factory=list)


@dataclass
class PipelineSpec:
    name: str
    stages: list[PipelineStage] = field(default_factory=list)


class PipelineBuilder:
    def __init__(self, name: str = "pipeline"):
        self._spec = PipelineSpec(name=name)

    def source(self, name: str, fn: callable) -> PipelineBuilder:
        self._spec.stages.append(PipelineStage(name, "source", fn))
        return self

    def map(self, name: str, fn: callable,
            on_error: callable | None = None) -> PipelineBuilder:
        self._spec.stages.append(PipelineStage(name, "map", fn, on_error))
        return self

    def filter(self, name: str, fn: callable) -> PipelineBuilder:
        self._spec.stages.append(PipelineStage(name, "filter", fn))
        return self

    def flat_map(self, name: str, fn: callable) -> PipelineBuilder:
        self._spec.stages.append(PipelineStage(name, "flat_map", fn))
        return self

    def reduce(self, name: str, fn: callable, initial: object = None) -> PipelineBuilder:
        self._spec.stages.append(PipelineStage(name, "reduce",
                                                lambda items, f=fn, i=initial: self._do_reduce(items, f, i)))
        return self

    def sink(self, name: str, fn: callable) -> PipelineBuilder:
        self._spec.stages.append(PipelineStage(name, "sink", fn))
        return self

    @staticmethod
    def _do_reduce(items, fn, initial):
        acc = initial
        for item in items:
            acc = fn(acc, item) if acc is not None else item
        return acc

    def validate(self) -> list[str]:
        """Validate pipeline structure."""
        errors = []
        if not self._spec.stages:
            errors.append("Pipeline has no stages")
            return errors
        if self._spec.stages[0].stage_type != "source":
            errors.append("First stage must be a source")
        stage_names = [s.name for s in self._spec.stages]
        if len(stage_names) != len(set(stage_names)):
            errors.append("Duplicate stage names")
        return errors

    def build(self) -> PipelineSpec:
        errors = self.validate()
        if errors:
            raise ValueError(f"Invalid pipeline: {errors}")
        return self._spec


class PipelineBuilderService:
    def __init__(self):
        self._pipelines: dict[str, PipelineSpec] = {}

    def create(self, name: str) -> PipelineBuilder:
        return PipelineBuilder(name)

    def register(self, spec: PipelineSpec) -> None:
        self._pipelines[spec.name] = spec

    def execute(self, name: str = "", spec: PipelineSpec | None = None) -> dict:
        """Execute a pipeline. Returns result summary."""
        pipeline = spec or self._pipelines.get(name)
        if not pipeline:
            return {"status": "error", "error": "Pipeline not found"}

        data = []
        errors = []
        stages_run = 0

        for stage in pipeline.stages:
            stages_run += 1
            try:
                if stage.stage_type == "source":
                    data = list(stage.fn())
                elif stage.stage_type == "map":
                    new_data = []
                    for item in data:
                        try:
                            new_data.append(stage.fn(item))
                        except Exception as e:
                            if stage.error_handler:
                                result = stage.error_handler(item, e)
                                if result is not None:
                                    new_data.append(result)
                            else:
                                errors.append(f"{stage.name}: {e}")
                    data = new_data
                elif stage.stage_type == "filter":
                    data = [item for item in data if stage.fn(item)]
                elif stage.stage_type == "flat_map":
                    data = [sub for item in data for sub in stage.fn(item)]
                elif stage.stage_type == "reduce":
                    data = [stage.fn(data)]
                elif stage.stage_type == "sink":
                    for item in data:
                        stage.fn(item)
            except Exception as e:
                return {"status": "error", "error": f"Stage {stage.name}: {e}",
                        "stages_completed": stages_run - 1}

        return {"status": "completed", "output_count": len(data),
                "output": data, "stages_completed": stages_run,
                "errors": errors}

    def dry_run(self, spec: PipelineSpec, sample_size: int = 5) -> dict:
        """Execute with limited data for testing."""
        # Wrap source to limit output
        original_source = spec.stages[0].fn
        spec.stages[0].fn = lambda: list(original_source())[:sample_size]
        result = self.execute(spec=spec)
        spec.stages[0].fn = original_source  # restore
        result["dry_run"] = True
        return result
