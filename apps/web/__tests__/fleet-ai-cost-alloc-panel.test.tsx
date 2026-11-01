import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCostAllocPanel } from "@/components/fleet-ai-cost-alloc-panel";
describe("FleetAiCostAllocPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiCostAllocPanel allocators={2} active={2} teams={30} totalUsd={1000000} allocatedPct={99} />);
    expect(container.textContent).toContain("Cost Allocation");
}); });
