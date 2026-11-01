import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SysTopologyOverview } from "@/components/sys-topology-overview";

describe("SysTopologyOverview", () => {
  it("renders topology", () => {
    const { container } = render(
      <SysTopologyOverview totalServices={5} totalConnections={4}
        layers={{
          frontend: { services: 1, healthy: 1, connections: 1 },
          backend: { services: 2, healthy: 2, connections: 3 },
          data: { services: 2, healthy: 1, connections: 0 },
        }} />
    );
    expect(container.textContent).toContain("System Topology");
    expect(container.textContent).toContain("5 services");
    expect(container.textContent).toContain("4 connections");
    expect(container.textContent).toContain("frontend");
    expect(container.textContent).toContain("backend");
    expect(container.textContent).toContain("data");
  });
});
