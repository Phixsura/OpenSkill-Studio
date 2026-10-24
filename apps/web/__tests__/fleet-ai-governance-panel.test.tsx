import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiGovernancePanel } from "@/components/fleet-ai-governance-panel";
describe("FleetAiGovernancePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiGovernancePanel frameworks={5} active={5} policies={100} reviews={5000} />);
    expect(container.textContent).toContain("AI Governance");
}); });
