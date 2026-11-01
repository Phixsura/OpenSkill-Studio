import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PipelineStatus } from "@/components/pipeline-status";

const pipeline = {
  pipelineId: "p1", version: "1.0.0", trigger: "push", status: "failed",
  stages: [
    { name: "lint", status: "passed", output: "" },
    { name: "test", status: "failed", output: "3 tests failed" },
    { name: "build", status: "skipped", output: "" },
  ],
};

describe("PipelineStatus", () => {
  it("renders pipeline", () => {
    const { container } = render(<PipelineStatus pipeline={pipeline} />);
    expect(container.textContent).toContain("v1.0.0");
    expect(container.textContent).toContain("failed");
    expect(container.textContent).toContain("3 tests failed");
    expect(container.textContent).toContain("lint");
    expect(container.textContent).toContain("test");
    expect(container.textContent).toContain("build");
  });
});
