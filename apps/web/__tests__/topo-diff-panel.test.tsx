import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TopoDiffPanel } from "@/components/topo-diff-panel";
describe("TopoDiffPanel", () => {
  it("renders", () => {
    const { container } = render(
      <TopoDiffPanel risk="medium" totalChanges={4}
        addedNodes={["new-svc"]} removedNodes={["old-svc"]}
        addedEdges={["api→new-svc"]} removedEdges={["api→old-svc"]} />
    );
    expect(container.textContent).toContain("Topology Diff");
    expect(container.textContent).toContain("medium risk");
    expect(container.textContent).toContain("4 changes");
    expect(container.textContent).toContain("+ node: new-svc");
    expect(container.textContent).toContain("- node: old-svc");
  });
});
