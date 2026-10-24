import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DataPipelineView } from "@/components/data-pipeline-view";

describe("DataPipelineView", () => {
  const steps = [
    { order: 1, name: "Extract", type: "extract", icon: "📥", status: "completed", recordsProcessed: 1000, durationMs: 500 },
    { order: 2, name: "Load", type: "load", icon: "📤", status: "running", recordsProcessed: 0, durationMs: 0 },
  ];
  it("renders pipeline", () => {
    const { container } = render(
      <DataPipelineView name="Import" steps={steps} progressPct={50} totalRecords={1000} completed={1} />
    );
    expect(container.textContent).toContain("Import");
    expect(container.textContent).toContain("Extract");
    expect(container.textContent).toContain("Load");
    expect(container.textContent).toContain("1/2 steps");
  });
});
