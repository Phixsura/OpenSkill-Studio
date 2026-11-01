import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SvcMapPanel } from "@/components/svc-map-panel";
describe("SvcMapPanel", () => {
  it("renders", () => {
    const { container } = render(
      <SvcMapPanel nodes={["gateway", "api", "db", "cache"]}
        entryPoints={["gateway"]} leafNodes={["db", "cache"]}
        edges={[
          { source: "gateway", destination: "api", requests: 10000, avgLatencyMs: 15, errorRate: 0.5 },
          { source: "api", destination: "db", requests: 5000, avgLatencyMs: 5, errorRate: 0.1 },
        ]} />
    );
    expect(container.textContent).toContain("Service Map");
    expect(container.textContent).toContain("4 nodes");
    expect(container.textContent).toContain("2 edges");
    expect(container.textContent).toContain("Entry: gateway");
    expect(container.textContent).toContain("Leaf: db, cache");
    expect(container.textContent).toContain("gateway → api");
  });
});
