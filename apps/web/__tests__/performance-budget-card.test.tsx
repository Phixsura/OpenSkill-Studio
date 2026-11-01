import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PerformanceBudgetCard } from "@/components/performance-budget-card";

describe("PerformanceBudgetCard", () => {
  it("within budget", () => {
    const { container } = render(<PerformanceBudgetCard withinBudget={true} score={100} violations={[]} />);
    expect(container.textContent).toContain("100%");
    expect(container.textContent).toContain("within budget");
  });
  it("shows violations", () => {
    const violations = [{ metric: "bundle_size", actual: 800, limit: 500, unit: "KB" }];
    const { container } = render(<PerformanceBudgetCard withinBudget={false} score={67} violations={violations} />);
    expect(container.textContent).toContain("bundle size");
    expect(container.textContent).toContain("800KB");
  });
});
