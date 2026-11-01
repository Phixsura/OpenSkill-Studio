import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CategoryTreeNav } from "@/components/category-tree-nav";

describe("CategoryTreeNav", () => {
  const categories = [
    { id: "connectors", label: "Connectors", icon: "🔗", children: [{ id: "crm", label: "CRM", icon: "📇" }] },
    { id: "automation", label: "Automation", icon: "⚡", children: [] },
  ];
  it("renders categories", () => {
    const { container } = render(<CategoryTreeNav categories={categories} activeId={null} onSelect={vi.fn()} />);
    expect(container.textContent).toContain("Connectors");
    expect(container.textContent).toContain("Automation");
  });
  it("expands children", () => {
    const fn = vi.fn();
    const { container } = render(<CategoryTreeNav categories={categories} activeId={null} onSelect={fn} />);
    fireEvent.click(container.querySelectorAll("button")[0]); // click Connectors
    expect(container.textContent).toContain("CRM");
  });
  it("selects category", () => {
    const fn = vi.fn();
    const { container } = render(<CategoryTreeNav categories={categories} activeId={null} onSelect={fn} />);
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith("connectors");
  });
});
