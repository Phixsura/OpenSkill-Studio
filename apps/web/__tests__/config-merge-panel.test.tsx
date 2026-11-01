import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ConfigMergePanel } from "@/components/config-merge-panel";

const mockResult = {
  merged: { theme: "dark", port: 3000, debug: false },
  conflicts: [{ path: "theme", values: ["light", "dark"], resolvedValue: "dark" }],
  sourcesMerged: 2,
};

describe("ConfigMergePanel", () => {
  it("renders merge button", () => {
    const { container } = render(<ConfigMergePanel result={null} sourceCount={3} />);
    expect(container.textContent).toContain("Merge 3 Sources");
  });

  it("shows merged result", () => {
    const { container } = render(<ConfigMergePanel result={mockResult} sourceCount={2} />);
    expect(container.textContent).toContain('"theme"');
    expect(container.textContent).toContain('"dark"');
  });

  it("shows conflicts", () => {
    const { getByText, container } = render(<ConfigMergePanel result={mockResult} sourceCount={2} />);
    fireEvent.click(getByText("Conflicts (1)"));
    expect(container.textContent).toContain("theme");
    expect(container.textContent).toContain("light");
  });

  it("calls onMerge", () => {
    const onMerge = vi.fn();
    const { getByText } = render(<ConfigMergePanel result={null} sourceCount={2} onMerge={onMerge} />);
    fireEvent.click(getByText("Merge 2 Sources"));
    expect(onMerge).toHaveBeenCalledWith("last_wins");
  });
});
