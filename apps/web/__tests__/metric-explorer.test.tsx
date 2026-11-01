import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MetricExplorer } from "@/components/metric-explorer";

describe("MetricExplorer", () => {
  it("renders explorer", () => {
    const { container } = render(
      <MetricExplorer totalMetrics={8} onSearch={vi.fn()}
        byType={{ counter: 2, gauge: 5, histogram: 1 }}
        metrics={[
          { name: "http_requests_total", type: "counter", unit: "requests", labels: ["method"] },
          { name: "cache_hit_ratio", type: "gauge", unit: "ratio", labels: ["cache"] },
        ]} />
    );
    expect(container.textContent).toContain("Metric Explorer");
    expect(container.textContent).toContain("counter: 2");
    expect(container.textContent).toContain("http_requests_total");
    expect(container.textContent).toContain("cache_hit_ratio");
    expect(container.textContent).toContain("gauge");
  });
});
