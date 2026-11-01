import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCostForecastPanel } from "@/components/fleet-cost-forecast-panel";
describe("FleetCostForecastPanel", () => { it("renders", () => {
    const { container } = render(<FleetCostForecastPanel daily={2000} monthly={60000} annual={720000} budgetWarning={true} />);
    expect(container.textContent).toContain("Cost Forecast");
    expect(container.textContent).toContain("Over $50K");
}); });
