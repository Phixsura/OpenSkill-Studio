import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { NetworkGraphView } from "@/components/network-graph-view";

describe("NetworkGraphView", () => {
  const nodes = [
    { id: "api", label: "API Gateway", type: "gateway", inDegree: 0, outDegree: 2, isRoot: true, isLeaf: false },
    { id: "db", label: "Database", type: "database", inDegree: 2, outDegree: 0, isRoot: false, isLeaf: true },
  ];
  it("renders graph info", () => {
    const { container } = render(
      <NetworkGraphView nodes={nodes} nodeCount={2} edgeCount={3} rootCount={1} leafCount={1} />
    );
    expect(container.textContent).toContain("API Gateway");
    expect(container.textContent).toContain("Database");
    expect(container.textContent).toContain("2 nodes");
    expect(container.textContent).toContain("1 entry points");
  });
});
