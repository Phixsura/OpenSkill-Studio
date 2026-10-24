import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PipelineMonitorDash } from "@/components/pipeline-monitor-dash";

describe("PipelineMonitorDash", () => {
  it("renders pipeline", () => {
    const { container } = render(
      <PipelineMonitorDash pipeline="etl-users" totalRecords={30000} totalErrors={5}
        healthy={false} bottleneck="transform"
        stages={[
          { name: "extract", records: 10000, errors: 0, throughputRps: 333 },
          { name: "transform", records: 10000, errors: 5, throughputRps: 83 },
          { name: "load", records: 9995, errors: 0, throughputRps: 222 },
        ]} />
    );
    expect(container.textContent).toContain("etl-users");
    expect(container.textContent).toContain("Errors");
    expect(container.textContent).toContain("bottleneck: transform");
    expect(container.textContent).toContain("extract");
    expect(container.textContent).toContain("333 rps");
  });
});
