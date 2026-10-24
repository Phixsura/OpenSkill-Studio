import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MetricExportPanel } from "@/components/metric-export-panel";
describe("MetricExportPanel", () => {
  it("renders", () => {
    const { container } = render(
      <MetricExportPanel total={2} byType={{ counter: 1, gauge: 1 }}
        metrics={[
          { name: "http_requests_total", type: "counter", value: 1000 },
          { name: "cpu_usage", type: "gauge", value: 0.75 },
        ]} />
    );
    expect(container.textContent).toContain("Metric Export");
    expect(container.textContent).toContain("2 metrics");
    expect(container.textContent).toContain("http_requests_total");
    expect(container.textContent).toContain("counter");
    expect(container.textContent).toContain("1000");
  });
});
