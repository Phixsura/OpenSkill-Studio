import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiInvestorV7Panel } from "@/components/fleet-ai-investor-v7-panel";
describe("FleetAiInvestorV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiInvestorV7Panel trackers={2} active={2} arr={2000000000} growth={60} ndr={150} rule40={90} />);
    expect(container.textContent).toContain("Investor v7");
}); });
