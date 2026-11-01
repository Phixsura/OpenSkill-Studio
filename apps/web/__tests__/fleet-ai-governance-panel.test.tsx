import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiGovernancePanel } from "@/components/fleet-ai-governance-panel";
describe("FleetAiGovernancePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiGovernancePanel frameworks={3} active={3} policies={500} violations={5} compliance={99.8} />);
    expect(container.textContent).toContain("AI Governance");
}); });
