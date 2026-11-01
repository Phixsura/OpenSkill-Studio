import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MetricRetentionPanel } from "@/components/metric-retention-panel";

describe("MetricRetentionPanel", () => {
  it("renders", () => {
    const { container } = render(
      <MetricRetentionPanel totalGb={50} needsOptimization={true} reductionPct={30}
        tiers={{
          raw: { retentionDays: 7, sizeGb: 30, resolution: "1s" },
          "1min": { retentionDays: 30, sizeGb: 15, resolution: "1m" },
          "1hour": { retentionDays: 365, sizeGb: 5, resolution: "1h" },
        }} />
    );
    expect(container.textContent).toContain("Metric Retention");
    expect(container.textContent).toContain("50 GB total");
    expect(container.textContent).toContain("Reduce 30%");
    expect(container.textContent).toContain("raw (1s)");
    expect(container.textContent).toContain("7d");
    expect(container.textContent).toContain("30 GB");
  });
});
