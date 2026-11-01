import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MetricAggChart } from "@/components/metric-agg-chart";

describe("MetricAggChart", () => {
  it("renders metrics", () => {
    const { container } = render(
      <MetricAggChart count={1000} avg={55} min={10} max={100} p50={60} p95={95} p99={99} window="1h" />
    );
    expect(container.textContent).toContain("Metrics (1h)");
    expect(container.textContent).toContain("1000 data points");
    expect(container.textContent).toContain("55");
    expect(container.textContent).toContain("P99");
    expect(container.textContent).toContain("99");
  });
});
