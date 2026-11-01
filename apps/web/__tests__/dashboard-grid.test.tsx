import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DashboardGrid } from "@/components/dashboard-grid";

const widgets = [
  { widgetId: "w1", title: "Total Extensions", widgetType: "counter", data: { value: 500 } },
  { widgetId: "w2", title: "Health", widgetType: "status", data: { status: "operational" } },
];

describe("DashboardGrid", () => {
  it("renders widgets", () => {
    const { container } = render(<DashboardGrid widgets={widgets} />);
    expect(container.textContent).toContain("Total Extensions");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("Operational");
  });
  it("empty state", () => {
    const { container } = render(<DashboardGrid widgets={[]} />);
    expect(container.textContent).toContain("Add widgets");
  });
});
