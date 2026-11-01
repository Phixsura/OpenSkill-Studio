import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ConfigDiffViewer } from "@/components/config-diff-viewer";

const mockDiffs = [
  { key: "theme", status: "changed" as const, oldValue: "dark", newValue: "light" },
  { key: "api_url", status: "added" as const, newValue: "https://api.new.com" },
  { key: "legacy_mode", status: "removed" as const, oldValue: "true" },
  { key: "timeout", status: "unchanged" as const, oldValue: "30", newValue: "30" },
];

describe("ConfigDiffViewer", () => {
  it("renders diff summary", () => {
    const { container } = render(
      <ConfigDiffViewer diffs={mockDiffs} fromVersion="1.0.0" toVersion="2.0.0" />
    );
    expect(container.textContent).toContain("Config Changes");
    expect(container.textContent).toContain("1.0.0 → 2.0.0");
    expect(container.textContent).toContain("+1 added");
    expect(container.textContent).toContain("−1 removed");
    expect(container.textContent).toContain("~1 changed");
  });

  it("shows changed values", () => {
    const { container } = render(
      <ConfigDiffViewer diffs={mockDiffs} fromVersion="1.0" toVersion="2.0" />
    );
    expect(container.textContent).toContain("- dark");
    expect(container.textContent).toContain("+ light");
  });

  it("calls onApply", () => {
    const onApply = vi.fn();
    const { getByText } = render(
      <ConfigDiffViewer diffs={mockDiffs} fromVersion="1.0" toVersion="2.0" onApply={onApply} />
    );
    fireEvent.click(getByText("✅ Apply Changes"));
    expect(onApply).toHaveBeenCalled();
  });

  it("hides unchanged entries from main view", () => {
    const { container } = render(
      <ConfigDiffViewer diffs={mockDiffs} fromVersion="1.0" toVersion="2.0" />
    );
    // unchanged "timeout" should not appear as a diff card
    const diffCards = container.querySelectorAll(".rounded-lg.border.p-3");
    expect(diffCards.length).toBe(3); // only added, removed, changed
  });
});
