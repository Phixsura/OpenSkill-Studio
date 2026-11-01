import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FilterChipBar } from "@/components/filter-chip-bar";

describe("FilterChipBar", () => {
  const chips = [
    { key: "category", value: "tools", label: "Category: tools", icon: "📂" },
    { key: "rating", value: "4+", label: "Rating: 4+", icon: "⭐" },
  ];
  it("renders", () => {
    const { container } = render(
      <FilterChipBar chips={chips} onRemove={vi.fn()} onClearAll={vi.fn()} />
    );
    expect(container.textContent).toContain("Filters:");
    expect(container.textContent).toContain("Category: tools");
    expect(container.textContent).toContain("⭐");
    expect(container.textContent).toContain("Clear all");
  });
  it("remove chip", () => {
    const fn = vi.fn();
    const { container } = render(
      <FilterChipBar chips={chips} onRemove={fn} onClearAll={vi.fn()} />
    );
    const removeBtns = Array.from(container.querySelectorAll("button")).filter(b => b.textContent === "×");
    fireEvent.click(removeBtns[0]);
    expect(fn).toHaveBeenCalledWith("category", "tools");
  });
  it("empty hidden", () => {
    const { container } = render(<FilterChipBar chips={[]} onRemove={vi.fn()} onClearAll={vi.fn()} />);
    expect(container.innerHTML).toBe("");
  });
});
