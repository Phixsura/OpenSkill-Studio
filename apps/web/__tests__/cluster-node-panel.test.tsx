import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ClusterNodePanel } from "@/components/cluster-node-panel";
describe("ClusterNodePanel", () => {
  it("renders", () => {
    const { container } = render(
      <ClusterNodePanel totalCpu={24} totalMemGb={96} ready={2}
        nodes={[
          { name: "n1", role: "control", cpu: 4, memoryGb: 16, status: "ready", cordoned: false },
          { name: "n2", role: "worker", cpu: 16, memoryGb: 64, status: "ready", cordoned: false },
          { name: "n3", role: "worker", cpu: 4, memoryGb: 16, status: "drained", cordoned: true },
        ]} />
    );
    expect(container.textContent).toContain("Cluster Nodes");
    expect(container.textContent).toContain("2/3 ready");
    expect(container.textContent).toContain("24 CPU");
    expect(container.textContent).toContain("n1");
    expect(container.textContent).toContain("control");
    expect(container.textContent).toContain("n3");
  });
});
