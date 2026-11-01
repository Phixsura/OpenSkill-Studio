import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MarketplaceCategoryGrid } from "@/components/marketplace-category-grid";

const cats = [{ name: "Tools", icon: "🔧", count: 50 }, { name: "Analytics", icon: "📊", count: 30 }];

describe("MarketplaceCategoryGrid", () => {
  it("renders categories", () => {
    const { container } = render(<MarketplaceCategoryGrid categories={cats} />);
    expect(container.textContent).toContain("Tools");
    expect(container.textContent).toContain("50 extensions");
  });
  it("calls onSelect", () => {
    const fn = vi.fn();
    const { getByText } = render(<MarketplaceCategoryGrid categories={cats} onSelect={fn} />);
    fireEvent.click(getByText("Tools"));
    expect(fn).toHaveBeenCalledWith("Tools");
  });
});
