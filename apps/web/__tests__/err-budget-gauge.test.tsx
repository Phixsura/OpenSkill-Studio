import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrBudgetGauge } from "@/components/err-budget-gauge";

describe("ErrBudgetGauge", () => {
  it("renders gauge", () => {
    const { container } = render(
      <ErrBudgetGauge consumedPct={50} remaining={500} allowed={1000}
        action="normal" exhausted={false} projectedAtEnd={100} dailyBurnPct={3.33} />
    );
    expect(container.textContent).toContain("Error Budget");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("500 remaining");
    expect(container.textContent).toContain("Normal");
    expect(container.textContent).toContain("3.33%/day");
  });
});
