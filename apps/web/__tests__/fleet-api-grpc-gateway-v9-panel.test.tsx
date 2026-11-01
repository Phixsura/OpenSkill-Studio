import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiGrpcGatewayV9Panel } from "@/components/fleet-api-grpc-gateway-v9-panel";
describe("FleetApiGrpcGatewayV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiGrpcGatewayV9Panel gateways={5} methods={200} />);
    expect(container.textContent).toContain("gRPC Gateway v9");
}); });
