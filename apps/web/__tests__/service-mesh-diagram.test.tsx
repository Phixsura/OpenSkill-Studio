import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ServiceMeshDiagram } from "@/components/service-mesh-diagram";

describe("ServiceMeshDiagram", () => {
  it("renders mesh", () => {
    const { container } = render(
      <ServiceMeshDiagram healthy={2} unhealthy={1}
        nodes={[
          { name: "api", port: 8080, replicas: 2, healthy: true },
          { name: "db", port: 5432, replicas: 1, healthy: true },
          { name: "cache", port: 6379, replicas: 1, healthy: false },
        ]}
        connections={[
          { from: "api", to: "db", protocol: "http", timeoutMs: 5000 },
        ]} />
    );
    expect(container.textContent).toContain("Service Mesh");
    expect(container.textContent).toContain("2 healthy");
    expect(container.textContent).toContain("1 unhealthy");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain(":8080");
    expect(container.textContent).toContain("db");
  });
});
