import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DependencyTreeView } from "@/components/dependency-tree-view";

const SIMPLE_TREE = {
  name: "my-app",
  version: "2.0.0",
  depth: 0,
  children: [
    {
      name: "react-pack",
      version: "1.5.0",
      depth: 1,
      constraint: "^1.0.0",
      status: "resolved" as const,
      children: [
        { name: "core-lib", version: "0.9.0", depth: 2, status: "resolved" as const, children: [] },
      ],
    },
    {
      name: "ui-toolkit",
      version: "3.0.0",
      depth: 1,
      status: "resolved" as const,
      children: [],
    },
  ],
};

const TREE_WITH_ISSUES = {
  name: "broken-app",
  version: "1.0.0",
  depth: 0,
  children: [
    { name: "good-dep", version: "1.0.0", depth: 1, status: "resolved" as const, children: [] },
    { name: "missing-dep", version: "0.0.0", depth: 1, status: "missing" as const, children: [] },
    {
      name: "conflict-dep",
      version: "2.0.0",
      depth: 1,
      status: "conflict" as const,
      constraint: "^1.0.0",
      children: [],
    },
  ],
};

describe("DependencyTreeView", () => {
  it("renders root package name and version", () => {
    const { container } = render(<DependencyTreeView root={SIMPLE_TREE} totalPackages={4} />);
    expect(container.textContent).toContain("my-app");
    expect(container.textContent).toContain("@2.0.0");
  });

  it("renders child dependencies", () => {
    const { container } = render(<DependencyTreeView root={SIMPLE_TREE} totalPackages={4} />);
    expect(container.textContent).toContain("react-pack");
    expect(container.textContent).toContain("ui-toolkit");
  });

  it("renders nested children (depth 2)", () => {
    const { container } = render(<DependencyTreeView root={SIMPLE_TREE} totalPackages={4} />);
    expect(container.textContent).toContain("core-lib");
  });

  it("shows constraint when present", () => {
    const { container } = render(<DependencyTreeView root={SIMPLE_TREE} totalPackages={4} />);
    expect(container.textContent).toContain("(^1.0.0)");
  });

  it("renders package count in header", () => {
    const { container } = render(<DependencyTreeView root={SIMPLE_TREE} totalPackages={4} />);
    expect(container.textContent).toContain("4 packages");
  });

  it("shows node count", () => {
    const { container } = render(<DependencyTreeView root={SIMPLE_TREE} totalPackages={4} />);
    expect(container.textContent).toContain("4 nodes");
  });

  it("shows All resolved when no issues", () => {
    const { container } = render(<DependencyTreeView root={SIMPLE_TREE} totalPackages={4} />);
    expect(container.textContent).toContain("All resolved");
  });

  it("shows missing count", () => {
    const { container } = render(<DependencyTreeView root={TREE_WITH_ISSUES} totalPackages={4} />);
    expect(container.textContent).toContain("1 missing");
  });

  it("shows conflict count", () => {
    const { container } = render(<DependencyTreeView root={TREE_WITH_ISSUES} totalPackages={4} />);
    expect(container.textContent).toContain("1 conflicts");
  });

  it("renders status icons", () => {
    const { container } = render(<DependencyTreeView root={TREE_WITH_ISSUES} totalPackages={4} />);
    expect(container.textContent).toContain("✓");
    expect(container.textContent).toContain("✗");
    expect(container.textContent).toContain("⚠");
  });

  it("calls onSelect when node clicked", () => {
    const onSelect = vi.fn();
    const { container } = render(
      <DependencyTreeView root={SIMPLE_TREE} totalPackages={4} onSelect={onSelect} />,
    );
    const links = Array.from(container.querySelectorAll("button")).filter((b) =>
      b.textContent?.includes("ui-toolkit"),
    );
    expect(links.length).toBeGreaterThan(0);
    fireEvent.click(links[0]);
    expect(onSelect).toHaveBeenCalledWith("ui-toolkit");
  });

  it("renders tree connectors", () => {
    const { container } = render(<DependencyTreeView root={SIMPLE_TREE} totalPackages={4} />);
    // Should have tree connector characters
    expect(container.textContent).toContain("├──");
    expect(container.textContent).toContain("└──");
  });

  it("renders Dependency Tree heading", () => {
    const { container } = render(<DependencyTreeView root={SIMPLE_TREE} totalPackages={4} />);
    expect(container.textContent).toContain("Dependency Tree");
  });
});
