import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PipelineVisualization } from "@/components/pipeline-visualization";

describe("PipelineVisualization", () => {
  it("renders pipeline", () => {
    const { container } = render(
      <PipelineVisualization name="Deploy" commit="abc12345" status="running" progressPct={67}
        stages={[
          { name: "build", status: "passed", durationMs: 5000 },
          { name: "test", status: "passed", durationMs: 3000 },
          { name: "deploy", status: "pending", durationMs: 0 },
        ]} />
    );
    expect(container.textContent).toContain("Deploy");
    expect(container.textContent).toContain("abc12345");
    expect(container.textContent).toContain("running");
    expect(container.textContent).toContain("67%");
    expect(container.textContent).toContain("build");
    expect(container.textContent).toContain("5.0s");
    expect(container.textContent).toContain("deploy");
  });
});
