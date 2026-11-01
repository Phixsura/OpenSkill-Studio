import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TopoHealthPanel } from "@/components/topo-health-panel";
describe("TopoHealthPanel", () => {
  it("renders", () => {
    const { container } = render(
      <TopoHealthPanel overall="critical" nodes={5} healthyNodes={3} edges={8}
        healthyEdges={6} criticalPathIssues={2} nodeHealthPct={60} />
    );
    expect(container.textContent).toContain("Topology: CRITICAL");
    expect(container.textContent).toContain("60% nodes healthy");
    expect(container.textContent).toContain("3/5");
    expect(container.textContent).toContain("6/8");
    expect(container.textContent).toContain("2");
  });
});
