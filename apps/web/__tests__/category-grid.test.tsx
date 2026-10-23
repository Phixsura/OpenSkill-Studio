import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CategoryGrid } from "@/components/category-grid";

describe("CategoryGrid", () => {
  const categories = [
    { id: "tools", name: "Developer Tools", icon: "🔧", count: 85, color: "blue" },
    { id: "security", name: "Security", icon: "🔒", count: 48, color: "red" },
    { id: "ai_ml", name: "AI & ML", icon: "🤖", count: 28, color: "cyan" },
  ];
  it("renders", () => {
    const { container } = render(
      <CategoryGrid categories={categories} totalApps={500} onCategoryClick={vi.fn()} />
    );
    expect(container.textContent).toContain("Browse Categories");
    expect(container.textContent).toContain("500 apps across 3 categories");
    expect(container.textContent).toContain("🔧");
    expect(container.textContent).toContain("Developer Tools");
    expect(container.textContent).toContain("85 apps");
    expect(container.textContent).toContain("🔒");
    expect(container.textContent).toContain("🤖");
  });
  it("click category", () => {
    const fn = vi.fn();
    const { container } = render(
      <CategoryGrid categories={categories} totalApps={500} onCategoryClick={fn} />
    );
    fireEvent.click(container.querySelectorAll("button")[1]);
    expect(fn).toHaveBeenCalledWith("security");
  });
});
