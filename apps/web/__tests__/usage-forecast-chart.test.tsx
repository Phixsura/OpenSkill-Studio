import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UsageForecastChart } from "@/components/usage-forecast-chart";

describe("UsageForecastChart", () => {
  it("renders forecast", () => {
    const { container } = render(
      <UsageForecastChart trend="growing" growthRatePct={20} slope={20}
        historicalPoints={5} predictions={[
          { month: 1, predicted: 200 }, { month: 2, predicted: 220 }, { month: 3, predicted: 240 },
        ]} />
    );
    expect(container.textContent).toContain("Usage Forecast");
    expect(container.textContent).toContain("growing");
    expect(container.textContent).toContain("20%/mo");
    expect(container.textContent).toContain("5 historical points");
    expect(container.textContent).toContain("240");
  });
});
