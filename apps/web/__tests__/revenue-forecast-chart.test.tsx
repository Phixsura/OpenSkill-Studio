import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RevenueForecastChart } from "@/components/revenue-forecast-chart";

describe("RevenueForecastChart", () => {
  const projections = [
    { month: 1, projected_revenue: 1331, confidence: 0.85 },
    { month: 2, projected_revenue: 1464, confidence: 0.75 },
  ];
  it("renders", () => {
    const { container } = render(
      <RevenueForecastChart lastMonth={1210} avgGrowthRate={10} projections={projections}
        totalHistorical={3310} totalProjected={2795} />
    );
    expect(container.textContent).toContain("Revenue Forecast");
    expect(container.textContent).toContain("+10%");
    expect(container.textContent).toContain("$3,310");
    expect(container.textContent).toContain("$2,795");
    expect(container.textContent).toContain("+1mo");
  });
});
