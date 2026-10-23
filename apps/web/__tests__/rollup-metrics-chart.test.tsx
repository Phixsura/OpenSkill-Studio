import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RollupMetricsChart } from "@/components/rollup-metrics-chart";

describe("RollupMetricsChart", () => {
  it("renders rollup", () => {
    const { container } = render(
      <RollupMetricsChart totalPoints={100} bucketMinutes={5}
        buckets={[
          { bucket: 0, count: 10, avg: 50, p95: 90, min: 10, max: 95 },
          { bucket: 300, count: 10, avg: 60, p95: 95, min: 15, max: 100 },
        ]} />
    );
    expect(container.textContent).toContain("Metrics Rollup");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("5min");
  });
});
