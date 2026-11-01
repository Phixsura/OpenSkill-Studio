import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrBudgetCard } from "@/components/err-budget-card";

describe("ErrBudgetCard", () => {
  it("renders", () => {
    const { container } = render(
      <ErrBudgetCard sloTarget={0.999} budgetTotal={1000} budgetConsumed={500}
        budgetRemaining={500} pctConsumed={50} status="ok" trend="stable" />
    );
    expect(container.textContent).toContain("Error Budget");
    expect(container.textContent).toContain("ok");
    expect(container.textContent).toContain("99.9%");
    expect(container.textContent).toContain("50% consumed");
    expect(container.textContent).toContain("500 remaining");
    expect(container.textContent).toContain("trend: stable");
  });
});
