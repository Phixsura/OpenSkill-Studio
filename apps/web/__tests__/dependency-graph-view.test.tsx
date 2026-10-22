import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DependencyGraphView } from "@/components/dependency-graph-view";

describe("DependencyGraphView", () => {
  it("renders graph", () => {
    const { container } = render(
      <DependencyGraphView
        nodes={[{ id: "a1", name: "Auth" }, { id: "a2", name: "CRM" }]}
        edges={[{ from: "a2", to: "a1", type: "depends_on" }]} />
    );
    expect(container.textContent).toContain("CRM");
    expect(container.textContent).toContain("depends on");
    expect(container.textContent).toContain("Auth");
  });
  it("empty state", () => {
    const { container } = render(<DependencyGraphView nodes={[]} edges={[]} />);
    expect(container.textContent).toContain("No dependencies");
  });
});
