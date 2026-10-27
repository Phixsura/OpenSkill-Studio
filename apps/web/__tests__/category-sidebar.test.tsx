import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CategorySidebar } from "@/components/category-sidebar";

const categories = [
  { categoryId: "tools", name: "Dev Tools", icon: "🛠️", extensionCount: 42, children: [{ categoryId: "linters", name: "Linters", icon: "🔍", extensionCount: 5 }] },
  { categoryId: "ui", name: "UI", icon: "🎨", extensionCount: 18 },
];

describe("CategorySidebar", () => {
  it("renders categories with children", () => {
    const { container } = render(<CategorySidebar categories={categories} selected="" />);
    expect(container.textContent).toContain("Dev Tools");
    expect(container.textContent).toContain("Linters");
    expect(container.textContent).toContain("42");
  });
  it("selects category", () => {
    const fn = vi.fn();
    const { container } = render(<CategorySidebar categories={categories} selected="" onSelect={fn} />);
    const btns = container.querySelectorAll("button");
    fireEvent.click(btns[1]); // Dev Tools
    expect(fn).toHaveBeenCalledWith("tools");
  });
});
