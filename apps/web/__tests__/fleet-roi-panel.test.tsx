import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRoiPanel } from "@/components/fleet-roi-panel";
describe("FleetRoiPanel", () => { it("renders", () => {
    const { container } = render(<FleetRoiPanel investment={100000} totalReturn={200000} roiPct={100} paybackMonths={6} positive={true} />);
    expect(container.textContent).toContain("Platform ROI");
    expect(container.textContent).toContain("100% ROI");
}); });
