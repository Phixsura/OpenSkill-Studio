import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGatewayPolicyV9Panel } from "@/components/fleet-gateway-policy-v9-panel";
describe("FleetGatewayPolicyV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetGatewayPolicyV9Panel policies={20} enforced={20} />);
    expect(container.textContent).toContain("Gateway Policy v9");
}); });
