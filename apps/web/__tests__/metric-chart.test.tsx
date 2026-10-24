import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MetricChart } from "@/components/metric-chart";

describe("MetricChart", () => {
  const buckets = [
    { timestamp: "2026-01-01T10", avg: 150, min: 100, max: 200, count: 2 },
    { timestamp: "2026-01-01T11", avg: 150, min: 150, max: 150, count: 1 },
  ];
  it("renders chart", () => {
    const { container } = render(
      <MetricChart buckets={buckets} globalAvg={150} globalMin={100} globalMax={200} interval="1h" />
    );
    expect(container.textContent).toContain("Metrics");
    expect(container.textContent).toContain("avg: 150");
    expect(container.textContent).toContain("2 intervals");
  });
});
