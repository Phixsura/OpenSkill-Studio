import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ServiceMeshTopology } from "@/components/service-mesh-topology";

describe("ServiceMeshTopology", () => {
  const nodes = [
    { id: "api", name: "API", type: "service", healthy: true },
    { id: "db", name: "Database", type: "datastore", healthy: false },
  ];
  const edges = [{ from: "api", to: "db", protocol: "grpc" }];
  it("renders", () => {
    const { container } = render(
      <ServiceMeshTopology nodes={nodes} edges={edges} meshHealth="degraded" />
    );
    expect(container.textContent).toContain("Service Mesh");
    expect(container.textContent).toContain("degraded");
    expect(container.textContent).toContain("API");
    expect(container.textContent).toContain("Database");
    expect(container.textContent).toContain("→ Database");
  });
});
