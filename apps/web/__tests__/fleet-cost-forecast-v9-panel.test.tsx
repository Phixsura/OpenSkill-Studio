import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCostForecastV9Panel } from "@/components/fleet-cost-forecast-v9-panel";
describe("FleetCostForecastV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCostForecastV9Panel forecasts={12} accurate={10} />);
    expect(container.textContent).toContain("Cost Forecast v9");
}); });
