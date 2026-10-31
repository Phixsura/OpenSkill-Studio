import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CostOptimizerResults } from "@/components/cost-optimizer-results";

describe("CostOptimizerResults", () => {
  const recs = [{ resource: "API Server", type: "downsize", reason: "Low usage", potential_savings: 70, priority: "high" }];
  it("renders", () => {
    const { container } = render(
      <CostOptimizerResults totalMonthlyCost={350} totalPotentialSavings={70} savingsPct={20}
        recommendations={recs} onApply={vi.fn()} />
    );
    expect(container.textContent).toContain("Cost Optimization");
    expect(container.textContent).toContain("$350/mo");
    expect(container.textContent).toContain("-$70");
    expect(container.textContent).toContain("API Server");
  });
  it("apply", () => {
    const fn = vi.fn();
    const { container } = render(
      <CostOptimizerResults totalMonthlyCost={350} totalPotentialSavings={70} savingsPct={20}
        recommendations={recs} onApply={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Apply")!);
    expect(fn).toHaveBeenCalledWith("API Server");
  });
});
