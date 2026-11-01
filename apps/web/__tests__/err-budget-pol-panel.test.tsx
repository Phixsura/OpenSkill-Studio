import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrBudgetPolPanel } from "@/components/err-budget-pol-panel";

describe("ErrBudgetPolPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ErrBudgetPolPanel budgetPct={85} freezeDeploys={false} daysToExhaustion={3}
        recommendedAction="reduce_deploy_frequency"
        triggered={[
          { policy: "slow_down", threshold: 70, action: "reduce_deploy_frequency", severity: "warning" },
        ]} />
    );
    expect(container.textContent).toContain("Error Budget Policy");
    expect(container.textContent).toContain("85% consumed");
    expect(container.textContent).toContain("3d left");
    expect(container.textContent).toContain("reduce deploy frequency");
    expect(container.textContent).toContain("slow_down");
  });
});
