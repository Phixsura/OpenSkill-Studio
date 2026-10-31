import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DashboardWidgetGrid } from "@/components/dashboard-widget-grid";

describe("DashboardWidgetGrid", () => {
  const widgets = [
    { widget_id: "w1", type: "metric_card", title: "Users",
      type_info: { icon: "📊", label: "Metric Card" }, position: { x: 0, y: 0, w: 1, h: 1 } },
  ];
  it("renders", () => {
    const { container } = render(
      <DashboardWidgetGrid widgets={widgets} columns={4} onRemove={vi.fn()} onAdd={vi.fn()} />
    );
    expect(container.textContent).toContain("Dashboard");
    expect(container.textContent).toContain("📊");
    expect(container.textContent).toContain("Users");
    expect(container.textContent).toContain("Metric Card");
  });
  it("remove", () => {
    const fn = vi.fn();
    const { container } = render(
      <DashboardWidgetGrid widgets={widgets} columns={4} onRemove={fn} onAdd={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "×")!);
    expect(fn).toHaveBeenCalledWith("w1");
  });
});
