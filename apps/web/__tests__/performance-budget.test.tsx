import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PerformanceBudget } from "@/components/performance-budget";

describe("PerformanceBudget", () => {
  const results = [
    { metric: "js_kb", limit: 200, actual: 150, over: false, pctOfBudget: 75 },
    { metric: "lcp_ms", limit: 2500, actual: 3500, over: true, pctOfBudget: 140 },
  ];
  it("renders budget results", () => {
    const { container } = render(
      <PerformanceBudget results={results} violations={1} withinBudget={false} />
    );
    expect(container.textContent).toContain("js_kb");
    expect(container.textContent).toContain("150 / 200");
    expect(container.textContent).toContain("lcp_ms");
    expect(container.textContent).toContain("1 over budget");
  });
});
