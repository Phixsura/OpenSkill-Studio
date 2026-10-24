import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ClusterNodeGrid } from "@/components/cluster-node-grid";

describe("ClusterNodeGrid", () => {
  it("renders nodes", () => {
    const { container } = render(
      <ClusterNodeGrid ready={2} pressure={1} totalCpuCores={20} avgCpuPct={64}
        nodes={[
          { name: "node-1", cpuCores: 8, memoryGb: 32, zone: "zone-a", cpuUsedPct: 40, memoryUsedPct: 50, status: "ready" },
          { name: "node-2", cpuCores: 8, memoryGb: 32, zone: "zone-a", cpuUsedPct: 60, memoryUsedPct: 70, status: "ready" },
          { name: "node-3", cpuCores: 4, memoryGb: 16, zone: "zone-b", cpuUsedPct: 92, memoryUsedPct: 88, status: "pressure" },
        ]} />
    );
    expect(container.textContent).toContain("Cluster Nodes");
    expect(container.textContent).toContain("2 ready");
    expect(container.textContent).toContain("1 pressure");
    expect(container.textContent).toContain("node-1");
    expect(container.textContent).toContain("zone-a");
    expect(container.textContent).toContain("20 cores");
  });
});
