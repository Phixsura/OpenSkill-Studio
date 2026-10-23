import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ServiceMeshDiagram } from "@/components/service-mesh-diagram";

describe("ServiceMeshDiagram", () => {
  const services = [
    { name: "api", port: 8080, protocol: "http", health: "healthy", depCount: 2, hasSidecar: true },
    { name: "db", port: 5432, protocol: "tcp", health: "healthy", depCount: 0, hasSidecar: false },
  ];
  it("renders mesh", () => {
    const { container } = render(
      <ServiceMeshDiagram services={services} policies={[]} totalConnections={2} mtlsEnabled={true} />
    );
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("db");
    expect(container.textContent).toContain("2 services");
    expect(container.textContent).toContain("mTLS");
  });
});
