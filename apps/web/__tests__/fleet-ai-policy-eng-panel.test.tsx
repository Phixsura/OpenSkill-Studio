import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPolicyEngPanel } from "@/components/fleet-ai-policy-eng-panel";
describe("FleetAiPolicyEngPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPolicyEngPanel engines={3} active={3} policies={200} evals={200000000} violations={0} />);
    expect(container.textContent).toContain("Policy Engine");
}); });
