import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ExtensionDependencyTree } from "@/components/extension-dependency-tree";

const mockTree = {
  id: "root", name: "my-extension", version: "2.0.0", status: "ok" as const,
  children: [
    { id: "sdk", name: "openskill-sdk", version: "3.1.0", status: "ok" as const,
      children: [
        { id: "http", name: "httpx", version: "0.24.0", status: "outdated" as const, children: [] },
      ] },
    { id: "lodash", name: "lodash", version: "4.17.10", status: "vulnerable" as const, children: [] },
    { id: "react", name: "react", version: "18.0.0", status: "ok" as const, children: [] },
  ],
};

describe("ExtensionDependencyTree", () => {
  it("renders root and direct children", () => {
    const { container } = render(<ExtensionDependencyTree root={mockTree} />);
    expect(container.textContent).toContain("Dependency Tree");
    expect(container.textContent).toContain("my-extension");
    expect(container.textContent).toContain("openskill-sdk");
    expect(container.textContent).toContain("lodash");
  });

  it("shows status counts", () => {
    const { container } = render(<ExtensionDependencyTree root={mockTree} />);
    expect(container.textContent).toContain("1 vulnerable");
    expect(container.textContent).toContain("1 outdated");
    expect(container.textContent).toContain("4 dependencies");
  });

  it("expands nested children on click", () => {
    const { container, getAllByText } = render(<ExtensionDependencyTree root={mockTree} />);
    // sdk has a ▶ toggle — click it to expand
    const toggles = container.querySelectorAll("button");
    const sdkToggle = Array.from(toggles).find((b) => b.textContent === "▶");
    if (sdkToggle) fireEvent.click(sdkToggle);
    expect(container.textContent).toContain("httpx");
  });

  it("calls onNodeSelect", () => {
    const onSelect = vi.fn();
    const { getByText } = render(<ExtensionDependencyTree root={mockTree} onNodeSelect={onSelect} />);
    fireEvent.click(getByText("lodash"));
    expect(onSelect).toHaveBeenCalledWith("lodash");
  });
});
