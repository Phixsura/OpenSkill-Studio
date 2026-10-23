import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CategoryGrid } from "@/components/category-grid";

describe("CategoryGrid", () => {
  const cats = [
    { id: "tools", name: "Developer Tools", icon: "🔧", description: "Build faster", count: 320 },
    { id: "ai", name: "AI & ML", icon: "🤖", description: "Intelligent", count: 130 },
  ];
  it("renders grid", () => {
    const { container } = render(<CategoryGrid categories={cats} totalApps={450} onSelect={vi.fn()} />);
    expect(container.textContent).toContain("Browse Categories");
    expect(container.textContent).toContain("Developer Tools");
    expect(container.textContent).toContain("AI & ML");
    expect(container.textContent).toContain("320 apps");
    expect(container.textContent).toContain("450");
  });
});
