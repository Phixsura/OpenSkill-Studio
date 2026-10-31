import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCostAttrPanel } from "@/components/fleet-ai-cost-attr-panel";
describe("FleetAiCostAttrPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiCostAttrPanel teams={10} totalMonthly={200000} topSpender="ML Team" />);
    expect(container.textContent).toContain("Cost Attribution");
    expect(container.textContent).toContain("ML Team");
}); });
