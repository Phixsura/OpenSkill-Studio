import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCapForecastPanel } from "@/components/fleet-cap-forecast-panel";
describe("FleetCapForecastPanel", () => { it("renders", () => {
    const { container } = render(<FleetCapForecastPanel daysUntilFull={20} urgent={true} currentPct={80} />);
    expect(container.textContent).toContain("Capacity Forecast");
    expect(container.textContent).toContain("20 days until full");
}); });
