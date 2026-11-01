import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { BuildPipelinePanel } from "@/components/build-pipeline-panel";

const mockBuilds = [
  { buildId: "b1", version: "1.0.0", trigger: "push", status: "passed" as const,
    stages: [
      { name: "lint", status: "passed" as const, durationMs: 500 },
      { name: "test", status: "passed" as const, durationMs: 3200 },
      { name: "build", status: "passed" as const, durationMs: 1500 },
    ],
    artifactUrl: "https://artifacts.example.com/ext-1/1.0.0.zip" },
  { buildId: "b2", version: "1.0.1", trigger: "manual", status: "failed" as const,
    stages: [
      { name: "lint", status: "passed" as const, durationMs: 400 },
      { name: "test", status: "failed" as const, durationMs: 2000, log: "2 tests failed" },
      { name: "build", status: "queued" as const, durationMs: 0 },
    ]},
];

describe("BuildPipelinePanel", () => {
  it("renders builds with stages", () => {
    const { container } = render(<BuildPipelinePanel builds={mockBuilds} />);
    expect(container.textContent).toContain("v1.0.0");
    expect(container.textContent).toContain("passed");
    expect(container.textContent).toContain("lint");
    expect(container.textContent).toContain("test");
  });

  it("shows artifact URL", () => {
    const { container } = render(<BuildPipelinePanel builds={mockBuilds} />);
    expect(container.textContent).toContain("artifacts.example.com");
  });

  it("calls onRetrigger for failed", () => {
    const onRetrigger = vi.fn();
    const { getByText } = render(<BuildPipelinePanel builds={mockBuilds} onRetrigger={onRetrigger} />);
    fireEvent.click(getByText("Retry"));
    expect(onRetrigger).toHaveBeenCalledWith("b2");
  });

  it("shows stage durations", () => {
    const { container } = render(<BuildPipelinePanel builds={mockBuilds} />);
    expect(container.textContent).toContain("3.2s");
    expect(container.textContent).toContain("500ms");
  });
});
