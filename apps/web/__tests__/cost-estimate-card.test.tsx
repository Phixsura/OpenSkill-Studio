import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CostEstimateCard } from "@/components/cost-estimate-card";

describe("CostEstimateCard", () => {
  it("shows monthly cost", () => {
    const { container } = render(<CostEstimateCard monthlyCost={12.50} dailyExecutions={100} perExecution={0.00042} tier="standard" />);
    expect(container.textContent).toContain("$12.50");
  });
  it("shows tier", () => {
    const { container } = render(<CostEstimateCard monthlyCost={0} dailyExecutions={0} perExecution={0} tier="premium" />);
    expect(container.textContent).toContain("premium");
  });
});
