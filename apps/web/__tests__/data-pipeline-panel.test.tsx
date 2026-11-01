import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DataPipelinePanel } from "@/components/data-pipeline-panel";

const mockPipelines = [
  { id: "p1", name: "User Import", status: "completed" as const,
    stages: [
      { name: "extract", stageType: "extract", status: "completed" as const, recordsIn: 100, recordsOut: 100, durationMs: 50 },
      { name: "validate", stageType: "validate", status: "completed" as const, recordsIn: 100, recordsOut: 85, durationMs: 30 },
      { name: "load", stageType: "load", status: "completed" as const, recordsIn: 85, recordsOut: 85, durationMs: 120 },
    ],
    totalRecords: 85, runCount: 5, lastDurationMs: 200 },
];

describe("DataPipelinePanel", () => {
  it("renders pipelines", () => {
    const { container } = render(<DataPipelinePanel pipelines={mockPipelines} />);
    expect(container.textContent).toContain("User Import");
    expect(container.textContent).toContain("3 stages");
    expect(container.textContent).toContain("×5");
  });

  it("expands to show stages", () => {
    const { getByText, container } = render(<DataPipelinePanel pipelines={mockPipelines} />);
    fireEvent.click(getByText("User Import"));
    expect(container.textContent).toContain("extract");
    expect(container.textContent).toContain("validate");
    expect(container.textContent).toContain("100→85");
  });

  it("calls onRun", () => {
    const onRun = vi.fn();
    const { getByText } = render(<DataPipelinePanel pipelines={mockPipelines} onRun={onRun} />);
    fireEvent.click(getByText("Run"));
    expect(onRun).toHaveBeenCalledWith("p1");
  });
});
