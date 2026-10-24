import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ChangelogPageViewer } from "@/components/changelog-page-viewer";

describe("ChangelogPageViewer", () => {
  it("renders entries", () => {
    const entries = [{ version: "2.0", released_at: "2026-06-01", changes: [{ type: "feat", description: "Dark mode" }], has_breaking: false }];
    const { container } = render(<ChangelogPageViewer entries={entries} page={1} totalPages={1} onPageChange={vi.fn()} />);
    expect(container.textContent).toContain("2.0");
    expect(container.textContent).toContain("Dark mode");
  });
  it("pagination", () => {
    const fn = vi.fn();
    const { container } = render(<ChangelogPageViewer entries={[]} page={2} totalPages={5} onPageChange={fn} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Next"))!);
    expect(fn).toHaveBeenCalledWith(3);
  });
});
