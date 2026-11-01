import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGrpcHealthV9Panel } from "@/components/fleet-grpc-health-v9-panel";
describe("FleetGrpcHealthV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetGrpcHealthV9Panel services={50} serving={50} />);
    expect(container.textContent).toContain("gRPC Health v9");
}); });
