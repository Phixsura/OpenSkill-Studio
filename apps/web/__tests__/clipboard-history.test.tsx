import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ClipboardHistoryPanel } from "@/components/clipboard-history";

describe("ClipboardHistoryPanel", () => {
  const items = [
    { preview: "const x = 42;", source: "copy", charCount: 14, timestamp: "2026-01-01" },
    { preview: "function hello()", source: "cut", charCount: 16, timestamp: "2026-01-01" },
  ];
  it("renders items", () => {
    const { container } = render(<ClipboardHistoryPanel items={items} total={2} onClear={vi.fn()} />);
    expect(container.textContent).toContain("const x = 42;");
    expect(container.textContent).toContain("2 items");
  });
  it("clear click", () => {
    const fn = vi.fn();
    const { container } = render(<ClipboardHistoryPanel items={items} total={2} onClear={fn} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Clear")!);
    expect(fn).toHaveBeenCalled();
  });
});
