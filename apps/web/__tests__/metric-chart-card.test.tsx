import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MetricChartCard } from "@/components/metric-chart-card";

describe("MetricChartCard", () => {
  const buckets = [
    { timestamp: 0, value: 10, count: 5 },
    { timestamp: 60, value: 15, count: 8 },
    { timestamp: 120, value: 12, count: 6 },
  ];
  it("renders", () => {
    const { container } = render(
      <MetricChartCard title="Requests" buckets={buckets} aggregation="avg" unit="/s" />
    );
    expect(container.textContent).toContain("Requests");
    expect(container.textContent).toContain("12/s");
    expect(container.textContent).toContain("avg");
  });
});
