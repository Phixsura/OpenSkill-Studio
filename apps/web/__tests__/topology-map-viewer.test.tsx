import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TopologyMapViewer } from "@/components/topology-map-viewer";

describe("TopologyMapViewer", () => {
  it("renders topology", () => {
    const { container } = render(
      <TopologyMapViewer healthy={3} nodeCount={3}
        nodes={[
          { name: "api", layer: "app", healthy: true },
          { name: "db", layer: "data", healthy: true },
          { name: "cache", layer: "data", healthy: false },
        ]}
        edges={[{ from: "api", to: "db", protocol: "http" }]}
        layers={{ app: ["api"], data: ["db", "cache"] }} />
    );
    expect(container.textContent).toContain("Service Topology");
    expect(container.textContent).toContain("3 nodes");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("db");
    expect(container.textContent).toContain("api→db");
  });
});
