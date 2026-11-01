import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ServiceMeshView } from "@/components/service-mesh-view";

describe("ServiceMeshView", () => {
  it("renders mesh", () => {
    const { container } = render(
      <ServiceMeshView totalConnections={4} meshHealth="degraded" criticalPath={["gateway"]} nodes={[
        { id: "gateway", name: "API Gateway", status: "healthy", rps: 5000, upstream: [], downstream: ["auth", "users"] },
        { id: "users", name: "User Service", status: "degraded", rps: 1500, upstream: ["gateway"], downstream: [] },
      ]} />
    );
    expect(container.textContent).toContain("Service Mesh");
    expect(container.textContent).toContain("degraded");
    expect(container.textContent).toContain("API Gateway");
    expect(container.textContent).toContain("5,000 rps");
    expect(container.textContent).toContain("Critical path");
  });
});
