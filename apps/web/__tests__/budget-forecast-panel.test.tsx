import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { BudgetForecastPanel } from "@/components/budget-forecast-panel";
describe("BudgetForecastPanel", () => {
  it("renders", () => {
    const { container } = render(
      <BudgetForecastPanel budgetTotal={1000} consumed={500} remaining={500}
        pctConsumed={50} dailyBurn={50} daysLeft={10} willExhaust={true}
        action="reduce_risk" urgency="high" />
    );
    expect(container.textContent).toContain("Budget Forecast");
    expect(container.textContent).toContain("10d left");
    expect(container.textContent).toContain("reduce risk");
    expect(container.textContent).toContain("50% consumed");
    expect(container.textContent).toContain("500 remaining");
    expect(container.textContent).toContain("50/day");
  });
});
