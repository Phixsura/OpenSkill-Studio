import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MeshRetryBudgetPanel } from "@/components/mesh-retry-budget-panel";
describe("MeshRetryBudgetPanel", () => {
  it("renders", () => {
    const { container } = render(
      <MeshRetryBudgetPanel budgetPct={20}
        budgets={[
          { key: "api→db", budget: 20, used: 15, usedPct: 75, exhausted: false },
          { key: "api→cache", budget: 10, used: 10, usedPct: 100, exhausted: true },
        ]} />
    );
    expect(container.textContent).toContain("Retry Budgets");
    expect(container.textContent).toContain("20% budget");
    expect(container.textContent).toContain("2 pairs");
    expect(container.textContent).toContain("15/20");
    expect(container.textContent).toContain("EXHAUSTED");
  });
});
