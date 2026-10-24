import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiGatewayHealthV9Panel } from "@/components/fleet-api-gateway-health-v9-panel";
describe("FleetApiGatewayHealthV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiGatewayHealthV9Panel gateways={5} rps={500000} />);
    expect(container.textContent).toContain("Gateway Health v9");
}); });
