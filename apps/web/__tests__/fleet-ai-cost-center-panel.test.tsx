import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCostCenterPanel } from "@/components/fleet-ai-cost-center-panel";
describe("FleetAiCostCenterPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiCostCenterPanel centers={3} active={3} teams={50} total={10000000} allocated={99.5} />);
    expect(container.textContent).toContain("Cost Center");
}); });
