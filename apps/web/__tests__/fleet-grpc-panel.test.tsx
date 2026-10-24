import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGrpcPanel } from "@/components/fleet-grpc-panel";
describe("FleetGrpcPanel", () => { it("renders", () => {
    const { container } = render(<FleetGrpcPanel total={10} serving={9} notServing={1} avgLatency={5} healthy={false} />);
    expect(container.textContent).toContain("gRPC Health");
    expect(container.textContent).toContain("1 not serving");
}); });
