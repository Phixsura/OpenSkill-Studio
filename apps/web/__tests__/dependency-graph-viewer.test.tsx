import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DependencyGraphViewer } from "@/components/dependency-graph-viewer";

const nodes = [
  { id: "app", name: "My App", version: "1.0.0", type: "root" as const },
  { id: "sdk", name: "OpenSkill SDK", version: "2.0.0", type: "direct" as const },
  { id: "utils", name: "Utils Lib", version: "3.1.0", type: "transitive" as const },
];

const edges = [
  { from: "app", to: "sdk", relation: "depends_on" as const },
  { from: "sdk", to: "utils", relation: "depends_on" as const },
];

describe("DependencyGraphViewer", () => {
  it("renders nodes and edge counts", () => {
    const { container } = render(
      <DependencyGraphViewer nodes={nodes} edges={edges} rootId="app" />
    );
    expect(container.textContent).toContain("Dependency Graph");
    expect(container.textContent).toContain("3 packages");
    expect(container.textContent).toContain("2 edges");
  });

  it("renders all nodes", () => {
    const { container } = render(
      <DependencyGraphViewer nodes={nodes} edges={edges} rootId="app" />
    );
    expect(container.textContent).toContain("My App");
    expect(container.textContent).toContain("OpenSkill SDK");
    expect(container.textContent).toContain("Utils Lib");
  });

  it("shows detail on node click", () => {
    const { container, getByText } = render(
      <DependencyGraphViewer nodes={nodes} edges={edges} rootId="app" />
    );
    fireEvent.click(getByText("OpenSkill SDK"));
    expect(container.textContent).toContain("Depends on:");
    expect(container.textContent).toContain("→ utils");
  });

  it("shows conflicts", () => {
    const conflictEdges = [...edges, { from: "sdk", to: "utils", relation: "conflicts_with" as const }];
    const { container } = render(
      <DependencyGraphViewer nodes={nodes} edges={conflictEdges} rootId="app" />
    );
    expect(container.textContent).toContain("1 conflicts");
  });
});
