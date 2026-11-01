import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DepGraphVisualizer } from "@/components/dep-graph-visualizer";

const mockNodes = [
  { id: "core", version: "1.0.0", dependencies: [], status: "ok" as const },
  { id: "lib-a", version: "2.1.0", dependencies: ["core"], status: "ok" as const },
  { id: "lib-b", version: "1.5.0", dependencies: ["core"], status: "conflict" as const },
];
const mockConflicts = [
  { dependency: "core", requestedBy: [
    { extension: "lib-a", version: "^1.0" },
    { extension: "lib-b", version: "^2.0" },
  ]},
];

describe("DepGraphVisualizer", () => {
  it("renders dependency nodes", () => {
    const { container } = render(
      <DepGraphVisualizer nodes={mockNodes} conflicts={mockConflicts}
        installOrder={["core", "lib-a", "lib-b"]} extensionName="MyApp" />
    );
    expect(container.textContent).toContain("core");
    expect(container.textContent).toContain("lib-a");
    expect(container.textContent).toContain("v2.1.0");
  });

  it("shows install order", () => {
    const { getByText, container } = render(
      <DepGraphVisualizer nodes={mockNodes} conflicts={mockConflicts}
        installOrder={["core", "lib-a", "lib-b"]} extensionName="MyApp" />
    );
    fireEvent.click(getByText("Install Order"));
    const items = container.querySelectorAll("li");
    expect(items.length).toBe(3);
  });

  it("shows conflicts", () => {
    const { getByText, container } = render(
      <DepGraphVisualizer nodes={mockNodes} conflicts={mockConflicts}
        installOrder={[]} extensionName="MyApp" />
    );
    fireEvent.click(getByText("Conflicts (1)"));
    expect(container.textContent).toContain("^1.0");
    expect(container.textContent).toContain("^2.0");
  });
});
