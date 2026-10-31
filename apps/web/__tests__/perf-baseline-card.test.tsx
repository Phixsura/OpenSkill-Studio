import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PerfBaselineCard } from "@/components/perf-baseline-card";

describe("PerfBaselineCard", () => {
  it("renders", () => {
    const { container } = render(
      <PerfBaselineCard hasRegression={true} comparisons={{
        avg: { baseline: 70, current: 100, delta: 30, pctChange: 42.9, regression: true },
        p99: { baseline: 150, current: 160, delta: 10, pctChange: 6.7, regression: false },
      }} />
    );
    expect(container.textContent).toContain("Performance Baseline");
    expect(container.textContent).toContain("Regression Detected");
    expect(container.textContent).toContain("avg");
    expect(container.textContent).toContain("70ms");
    expect(container.textContent).toContain("100ms");
    expect(container.textContent).toContain("+42.9%");
  });
});
