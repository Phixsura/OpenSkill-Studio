import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPolicyEngineV9Panel } from "@/components/fleet-policy-engine-v9-panel";
describe("FleetPolicyEngineV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetPolicyEngineV9Panel policies={100} violations={0} />);
    expect(container.textContent).toContain("Policy Engine v9");
}); });
