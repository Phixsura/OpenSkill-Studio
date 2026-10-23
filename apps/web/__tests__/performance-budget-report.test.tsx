import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PerformanceBudgetReport } from "@/components/performance-budget-report";

describe("PerformanceBudgetReport", () => {
  const results = [
    { metric: "js_size_kb", budget: 300, actual: 250, over_budget: false, usage_pct: 83.3 },
    { metric: "lcp_ms", budget: 2500, actual: 4000, over_budget: true, usage_pct: 160 },
  ];
  it("renders", () => {
    const { container } = render(
      <PerformanceBudgetReport results={results} violations={1} allWithin={false} />
    );
    expect(container.textContent).toContain("Performance Budget");
    expect(container.textContent).toContain("⚠️ 1 over");
    expect(container.textContent).toContain("JS Size");
    expect(container.textContent).toContain("✓");
    expect(container.textContent).toContain("✗");
    expect(container.textContent).toContain("250 / 300");
  });
});
