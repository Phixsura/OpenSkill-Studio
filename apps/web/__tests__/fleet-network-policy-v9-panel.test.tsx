import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetNetworkPolicyV9Panel } from "@/components/fleet-network-policy-v9-panel";
describe("FleetNetworkPolicyV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetNetworkPolicyV9Panel policies={80} violations={0} />);
    expect(container.textContent).toContain("Network Policy v9");
}); });
