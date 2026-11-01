import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PipelineBuilder } from "@/components/pipeline-builder";

describe("PipelineBuilder", () => {
  it("renders pipeline", () => {
    const { container } = render(
      <PipelineBuilder name="User ETL" status="completed" inputCount={100} outputCount={42} onRun={vi.fn()}
        steps={[
          { name: "Filter Active", action: "filter", field: "status" },
          { name: "Sort Name", action: "sort", field: "name" },
        ]} />
    );
    expect(container.textContent).toContain("User ETL");
    expect(container.textContent).toContain("2 steps");
    expect(container.textContent).toContain("100 → 42");
    expect(container.textContent).toContain("Filter Active");
    expect(container.textContent).toContain("Sort Name");
    expect(container.textContent).toContain("Done");
  });
});
