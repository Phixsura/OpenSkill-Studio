import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CategoryChipBar } from "@/components/category-chip-bar";

describe("CategoryChipBar", () => {
  const chips = [
    { id: "all", label: "All", icon: "📦", active: false, count: null },
    { id: "tools", label: "Tools", icon: "🔧", active: true, count: 85 },
    { id: "security", label: "Security", icon: "🔒", active: false, count: 48 },
  ];
  it("renders", () => {
    const { container } = render(<CategoryChipBar chips={chips} onSelect={vi.fn()} />);
    expect(container.textContent).toContain("All");
    expect(container.textContent).toContain("🔧");
    expect(container.textContent).toContain("Tools");
    expect(container.textContent).toContain("85");
    expect(container.textContent).toContain("🔒");
  });
  it("select", () => {
    const fn = vi.fn();
    const { container } = render(<CategoryChipBar chips={chips} onSelect={fn} />);
    fireEvent.click(container.querySelectorAll("button")[2]);
    expect(fn).toHaveBeenCalledWith("security");
  });
});
