import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ClusterOptPanel } from "@/components/cluster-opt-panel";
describe("ClusterOptPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ClusterOptPanel cpuUtilPct={56} memUtilPct={55} recommendation="optimal"
        nodes={2} pods={5} totalCpu={16} totalMemGb={64} />
    );
    expect(container.textContent).toContain("Cluster Optimizer");
    expect(container.textContent).toContain("optimal");
    expect(container.textContent).toContain("2 nodes");
    expect(container.textContent).toContain("5 pods");
    expect(container.textContent).toContain("CPU");
    expect(container.textContent).toContain("56%");
  });
});
