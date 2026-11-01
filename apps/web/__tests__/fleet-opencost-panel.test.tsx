import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetOpencostPanel } from "@/components/fleet-opencost-panel";
describe("FleetOpencostPanel", () => { it("renders", () => {
    const { container } = render(<FleetOpencostPanel namespaces={20} dailyCost={500} idleCost={100} efficiency={80} />);
    expect(container.textContent).toContain("OpenCost");
    expect(container.textContent).toContain("80% efficient");
}); });
