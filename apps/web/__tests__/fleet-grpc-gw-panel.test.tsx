import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGrpcGwPanel } from "@/components/fleet-grpc-gw-panel";
describe("FleetGrpcGwPanel", () => { it("renders", () => {
    const { container } = render(<FleetGrpcGwPanel gateways={5} active={5} rps={25000} transcoded={5000000} />);
    expect(container.textContent).toContain("gRPC Gateway");
}); });
