import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PipeMonitorDash } from "@/components/pipe-monitor-dash";

describe("PipeMonitorDash", () => {
  it("renders", () => {
    const { container } = render(
      <PipeMonitorDash successRate={95} totalRows={50000} throughput={2000} healthy={true}
        runs={[
          { name: "etl-users", status: "success", rowsProcessed: 30000, durationMs: 5000 },
          { name: "etl-orders", status: "failed", rowsProcessed: 0, durationMs: 1000 },
        ]} />
    );
    expect(container.textContent).toContain("Pipeline Monitor");
    expect(container.textContent).toContain("95% success");
    expect(container.textContent).toContain("2,000 rows/s");
    expect(container.textContent).toContain("50,000 total rows");
    expect(container.textContent).toContain("etl-users");
    expect(container.textContent).toContain("30,000 rows");
  });
});
