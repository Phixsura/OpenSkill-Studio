import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DepGraphViewer } from "@/components/dep-graph-viewer";

describe("DepGraphViewer", () => {
  it("renders phases", () => {
    const { container } = render(
      <DepGraphViewer nodeCount={4} edgeCount={4} hasCycle={false} cycleNodes={[]}
        phases={[["db", "cache"], ["api"], ["worker"]]} />
    );
    expect(container.textContent).toContain("Dependency Graph");
    expect(container.textContent).toContain("4 nodes");
    expect(container.textContent).toContain("Phase 1");
    expect(container.textContent).toContain("db");
    expect(container.textContent).toContain("worker");
  });

  it("renders cycle", () => {
    const { container } = render(
      <DepGraphViewer nodeCount={2} edgeCount={2} hasCycle={true} cycleNodes={["a", "b"]} phases={[]} />
    );
    expect(container.textContent).toContain("Cycle");
    expect(container.textContent).toContain("Circular dependency");
  });
});
