import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCapacityForecastV9Panel } from "@/components/fleet-capacity-forecast-v9-panel";
describe("FleetCapacityForecastV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCapacityForecastV9Panel resources={50} atRisk={0} />);
    expect(container.textContent).toContain("Capacity Forecast v9");
}); });
