import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ClusterUtilView } from "@/components/cluster-util-view";

describe("ClusterUtilView", () => {
  it("renders", () => {
    const { container } = render(
      <ClusterUtilView clusterCount={2} cpuPct={50} memPct={64}
        cpuCapacity={200} cpuUsed={100} memCapacityGb={512} memUsedGb={328}
        overallHealth="healthy" />
    );
    expect(container.textContent).toContain("Cluster Utilization");
    expect(container.textContent).toContain("2 clusters");
    expect(container.textContent).toContain("healthy");
    expect(container.textContent).toContain("100/200 cores");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("328/512 GB");
  });
});
