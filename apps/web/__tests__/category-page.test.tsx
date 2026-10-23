import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CategoryPage } from "@/components/category-page";

describe("CategoryPage", () => {
  const category = { id: "tools", name: "Developer Tools", icon: "🔧", description: "Build faster" };
  const apps = [{ id: "a1", name: "Editor", icon: "📝", tagline: "Code editor", rating: 4.5, downloads: 5000 }];
  it("renders category", () => {
    const { container } = render(
      <CategoryPage category={category} apps={apps} total={1} sortBy="popular"
        onSort={vi.fn()} onSelectApp={vi.fn()} />
    );
    expect(container.textContent).toContain("Developer Tools");
    expect(container.textContent).toContain("Build faster");
    expect(container.textContent).toContain("Editor");
    expect(container.textContent).toContain("1 apps");
  });
});
