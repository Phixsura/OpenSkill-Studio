import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WidgetCatalog } from "@/components/widget-catalog";

describe("WidgetCatalog", () => {
  const widgets = [
    { id: "stat-card", name: "Stat Card", category: "display", preview: "📊" },
    { id: "modal", name: "Modal", category: "overlay", preview: "🪟" },
  ];
  it("renders widgets", () => {
    const { container } = render(<WidgetCatalog widgets={widgets} onSelect={vi.fn()} />);
    expect(container.textContent).toContain("Stat Card");
    expect(container.textContent).toContain("Modal");
  });
  it("selects widget", () => {
    const fn = vi.fn();
    const { container } = render(<WidgetCatalog widgets={widgets} onSelect={fn} />);
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith("stat-card");
  });
});
