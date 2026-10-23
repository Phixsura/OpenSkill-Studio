import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DependencyGraph } from "@/components/dependency-graph";

describe("DependencyGraph", () => {
  const nodes = [
    { name: "react", version: "18.3.0", size_kb: 120, dep_count: 1 },
    { name: "lodash", version: "4.17.21", size_kb: 70, dep_count: 0 },
  ];
  const edges = [{ from: "app", to: "react" }];
  it("renders packages", () => {
    const { container } = render(
      <DependencyGraph nodes={nodes} edges={edges} totalSizeKb={190} maxDepth={2} />
    );
    expect(container.textContent).toContain("react");
    expect(container.textContent).toContain("lodash");
    expect(container.textContent).toContain("2 packages");
    expect(container.textContent).toContain("depth 2");
  });
});
