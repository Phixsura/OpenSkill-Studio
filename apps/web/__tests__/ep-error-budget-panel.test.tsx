import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EpErrorBudgetPanel } from "@/components/ep-error-budget-panel";
describe("EpErrorBudgetPanel", () => {
  it("renders", () => {
    const { container } = render(
      <EpErrorBudgetPanel exhaustedCount={1} allWithinBudget={false}
        endpoints={[
          { endpoint: "/api/users", budget: 100, consumed: 50, pctConsumed: 50, exhausted: false },
          { endpoint: "/api/orders", budget: 10, consumed: 20, pctConsumed: 200, exhausted: true },
        ]} />
    );
    expect(container.textContent).toContain("Endpoint Error Budgets");
    expect(container.textContent).toContain("1 exhausted");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("50/100");
    expect(container.textContent).toContain("/api/orders");
    expect(container.textContent).toContain("20/10");
  });
});
