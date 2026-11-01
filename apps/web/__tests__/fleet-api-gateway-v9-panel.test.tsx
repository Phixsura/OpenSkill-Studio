import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiGatewayV9Panel } from "@/components/fleet-api-gateway-v9-panel";
describe("FleetApiGatewayV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiGatewayV9Panel routes={100} rps={500000} />);
    expect(container.textContent).toContain("API Gateway v9");
}); });
