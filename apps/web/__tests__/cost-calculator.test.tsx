import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CostCalculator } from "@/components/cost-calculator";

describe("CostCalculator", () => {
  const tiers = [{ name: "Free", from: 0, to: 1000, rate: 0 }, { name: "Paid", from: 1000, to: null, rate: 0.01 }];
  const onCalc = () => ({ totalCost: 0, breakdown: [{ tier: "Free", units: 1000, rate: 0, cost: 0 }] });
  it("renders calculator", () => {
    const { container } = render(<CostCalculator tiers={tiers} onCalculate={onCalc} />);
    expect(container.textContent).toContain("Cost Estimator");
    expect(container.textContent).toContain("$0.00");
    expect(container.textContent).toContain("Free");
  });
});
