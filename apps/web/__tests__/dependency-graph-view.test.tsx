import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DependencyGraphView } from "@/components/dependency-graph-view";

describe("DependencyGraphView", () => {
  const nodes = [
    { id: "root", name: "MyApp", type: "root" },
    { id: "d1", name: "Auth SDK", type: "dependency", version: "2.0" },
    { id: "d1a", name: "Crypto", type: "transitive" },
  ];
  const edges = [
    { from: "root", to: "d1", kind: "required" },
    { from: "d1", to: "d1a", kind: "transitive" },
  ];
  it("renders graph", () => {
    const { container } = render(
      <DependencyGraphView appName="MyApp" nodes={nodes} edges={edges} totalDependencies={2} />
    );
    expect(container.textContent).toContain("Dependencies");
    expect(container.textContent).toContain("MyApp");
    expect(container.textContent).toContain("Auth SDK");
    expect(container.textContent).toContain("Crypto");
    expect(container.textContent).toContain("2 total");
  });
});
