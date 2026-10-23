import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ChangelogWidget } from "@/components/changelog-widget";

describe("ChangelogWidget", () => {
  it("renders entries", () => {
    const entries = [{ version: "2.0", date: "2026-06-01", highlights: [{ type: "feat", text: "Dark mode" }], total_changes: 3 }];
    const { container } = render(<ChangelogWidget appName="App" entries={entries} hasMore={false} />);
    expect(container.textContent).toContain("2.0");
    expect(container.textContent).toContain("Dark mode");
    expect(container.textContent).toContain("+2 more");
  });
  it("view all", () => {
    const fn = vi.fn();
    const { container } = render(<ChangelogWidget appName="App" entries={[]} hasMore={true} onViewAll={fn} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
});
