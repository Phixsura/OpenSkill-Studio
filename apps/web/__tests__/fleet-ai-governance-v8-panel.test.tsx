import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiGovernanceV8Panel } from "@/components/fleet-ai-governance-v8-panel";
describe("FleetAiGovernanceV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiGovernanceV8Panel frameworks={5} active={5} policies={5000} compliance={99.9} approvals={2000} />);
    expect(container.textContent).toContain("Governance v8");
}); });
