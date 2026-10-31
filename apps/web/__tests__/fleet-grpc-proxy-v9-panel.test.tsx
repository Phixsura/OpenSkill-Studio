import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGrpcProxyV9Panel } from "@/components/fleet-grpc-proxy-v9-panel";
describe("FleetGrpcProxyV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetGrpcProxyV9Panel services={50} rps={100000} />);
    expect(container.textContent).toContain("gRPC Proxy v9");
}); });
