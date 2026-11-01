import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDashboardWidgetCard from "../src/components/api-dashboard-widget-card";

const widgets = [
  { widget_id: "w1", widget_type: "chart", title: "Revenue", data_source: "/api/revenue", refresh_interval: 60, refresh_count: 100 },
  { widget_id: "w2", widget_type: "metric", title: "Users", data_source: "/api/users", refresh_interval: 30, refresh_count: 200 },
];

describe("APIDashboardWidgetCard", () => {
  it("renders header and count", () => {
    const { container } = render(<APIDashboardWidgetCard widgets={widgets} appName="App" />);
    expect(container.textContent).toContain("Dashboard Widgets");
    expect(container.textContent).toContain("2 widgets");
  });

  it("shows titles with type icons", () => {
    const { container } = render(<APIDashboardWidgetCard widgets={widgets} appName="App" />);
    expect(container.textContent).toContain("Revenue");
    expect(container.textContent).toContain("📈");
    expect(container.textContent).toContain("🔢");
  });

  it("shows empty state", () => {
    const { container } = render(<APIDashboardWidgetCard widgets={[]} appName="App" />);
    expect(container.textContent).toContain("No widgets");
  });
});
