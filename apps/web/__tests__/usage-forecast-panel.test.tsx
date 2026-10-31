import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UsageForecastPanel } from "@/components/usage-forecast-panel";
describe("UsageForecastPanel", () => {
  it("renders", () => {
    const { container } = render(
      <UsageForecastPanel currentDaily={10000} projected30d={15000} trend="growing" growthRatePct={5.5} />
    );
    expect(container.textContent).toContain("Usage Forecast");
    expect(container.textContent).toContain("growing");
    expect(container.textContent).toContain("+5.5%");
    expect(container.textContent).toContain("10,000/day");
    expect(container.textContent).toContain("15,000/day");
  });
});
