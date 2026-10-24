import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TopoDiffViewer } from "@/components/topo-diff-viewer";

describe("TopoDiffViewer", () => {
  it("renders", () => {
    const { container } = render(
      <TopoDiffViewer totalChanges={4} breaking={true}
        nodesAdded={["queue"]} nodesRemoved={["cache"]}
        edgesAdded={["api→queue"]} edgesRemoved={["api→cache"]} />
    );
    expect(container.textContent).toContain("Topology Diff");
    expect(container.textContent).toContain("4 changes");
    expect(container.textContent).toContain("Breaking");
    expect(container.textContent).toContain("+ node: queue");
    expect(container.textContent).toContain("- node: cache");
    expect(container.textContent).toContain("+ edge: api→queue");
  });
});
