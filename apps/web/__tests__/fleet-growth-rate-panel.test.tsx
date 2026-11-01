import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGrowthRatePanel } from "@/components/fleet-growth-rate-panel";
describe("FleetGrowthRatePanel", () => { it("renders", () => {
    const { container } = render(<FleetGrowthRatePanel avgRate={150} latestRate={200} accelerating={true} />);
    expect(container.textContent).toContain("Growth Rate");
    expect(container.textContent).toContain("Accelerating");
}); });
