import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PipelineMonitor } from "@/components/pipeline-monitor";

describe("PipelineMonitor", () => {
  it("renders pipeline", () => {
    const { container } = render(
      <PipelineMonitor pipelineName="daily_etl" status="completed" durationDisplay="2.0s"
        totalRecords={29000} steps={[
          { name: "extract", type: "extract", status: "completed", durationMs: 500, records: 10000, error: null },
          { name: "transform", type: "transform", status: "completed", durationMs: 1200, records: 9500, error: null },
          { name: "load", type: "load", status: "completed", durationMs: 300, records: 9500, error: null },
        ]} />
    );
    expect(container.textContent).toContain("daily_etl");
    expect(container.textContent).toContain("completed");
    expect(container.textContent).toContain("2.0s");
    expect(container.textContent).toContain("extract");
    expect(container.textContent).toContain("29,000");
  });
});
