import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PipelineStageViewer } from "@/components/pipeline-stage-viewer";

describe("PipelineStageViewer", () => {
  it("renders", () => {
    const { container } = render(
      <PipelineStageViewer totalMs={150} passed={2} failed={true}
        stages={[
          { name: "extract", status: "success", durationMs: 50 },
          { name: "transform", status: "failed", durationMs: 100, error: "bad data" },
          { name: "load", status: "skipped", durationMs: 0 },
        ]} />
    );
    expect(container.textContent).toContain("Pipeline Stages");
    expect(container.textContent).toContain("2/3 passed");
    expect(container.textContent).toContain("150ms");
    expect(container.textContent).toContain("extract");
    expect(container.textContent).toContain("transform");
    expect(container.textContent).toContain("load");
  });
});
