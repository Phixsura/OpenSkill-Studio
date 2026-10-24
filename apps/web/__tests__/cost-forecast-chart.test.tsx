import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CostForecastChart } from "@/components/cost-forecast-chart";

describe("CostForecastChart", () => {
  it("renders forecast", () => {
    const { container } = render(
      <CostForecastChart currentMonthly={1300} avgMonthlyGrowth={100}
        totalProjected={4500} trend="increasing"
        forecast={[
          { month: 1, projectedCost: 1400, confidence: 90 },
          { month: 2, projectedCost: 1500, confidence: 85 },
          { month: 3, projectedCost: 1600, confidence: 80 },
        ]} />
    );
    expect(container.textContent).toContain("Cost Forecast");
    expect(container.textContent).toContain("increasing");
    expect(container.textContent).toContain("$1,300");
    expect(container.textContent).toContain("$4,500");
    expect(container.textContent).toContain("M+1");
    expect(container.textContent).toContain("90% conf");
  });
});
