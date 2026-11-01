import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { BookmarkListPanel } from "@/components/bookmark-list-panel";

const bms = [
  { extensionId: "ext-slack", collection: "tools", note: "Great tool", tags: ["comm"] },
  { extensionId: "ext-github", collection: "dev", note: "", tags: ["ci"] },
];

describe("BookmarkListPanel", () => {
  it("renders bookmarks", () => {
    const { container } = render(<BookmarkListPanel bookmarks={bms} collections={["tools", "dev"]} />);
    expect(container.textContent).toContain("ext-slack");
    expect(container.textContent).toContain("2 saved");
  });
  it("calls onRemove", () => {
    const fn = vi.fn();
    const { container } = render(<BookmarkListPanel bookmarks={bms} collections={[]} onRemove={fn} />);
    const del = container.querySelector("button.text-xs.text-red-500");
    if (del) fireEvent.click(del);
    expect(fn).toHaveBeenCalled();
  });
});
