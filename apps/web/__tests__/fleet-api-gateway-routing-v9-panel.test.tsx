import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiGatewayRoutingV9Panel } from "@/components/fleet-api-gateway-routing-v9-panel";
describe("FleetApiGatewayRoutingV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiGatewayRoutingV9Panel routes={50} rps={500000} />);
    expect(container.textContent).toContain("Gateway Routing v9");
}); });
