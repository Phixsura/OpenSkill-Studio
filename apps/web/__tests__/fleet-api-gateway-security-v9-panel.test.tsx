import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiGatewaySecurityV9Panel } from "@/components/fleet-api-gateway-security-v9-panel";
describe("FleetApiGatewaySecurityV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiGatewaySecurityV9Panel gateways={5} waf={5} />);
    expect(container.textContent).toContain("Gateway Security v9");
}); });
