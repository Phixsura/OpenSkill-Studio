import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCostGovV7Panel } from "@/components/fleet-ai-cost-gov-v7-panel";
describe("FleetAiCostGovV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiCostGovV7Panel systems={3} active={3} budgets={100} spend={20000000} within={true} />);
    expect(container.textContent).toContain("Cost Governance v7");
}); });
