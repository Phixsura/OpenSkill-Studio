import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetVpnGatewayV9Panel } from "@/components/fleet-vpn-gateway-v9-panel";
describe("FleetVpnGatewayV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetVpnGatewayV9Panel tunnels={10} up={10} />);
    expect(container.textContent).toContain("VPN Gateway v9");
}); });
