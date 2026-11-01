import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DepVizPanel } from "@/components/dep-viz-panel";
describe("DepVizPanel", () => {
  it("renders", () => {
    const { container } = render(
      <DepVizPanel nodes={4} edges={3} density={0.25}
        mostDependedOn="db" mostDependent="api"
        mermaid="graph LR\n    api --> db\n    api --> cache" />
    );
    expect(container.textContent).toContain("Dependency Graph");
    expect(container.textContent).toContain("4 nodes");
    expect(container.textContent).toContain("3 edges");
    expect(container.textContent).toContain("db");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("graph LR");
  });
});
