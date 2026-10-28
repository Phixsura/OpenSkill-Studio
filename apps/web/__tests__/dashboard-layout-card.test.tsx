import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import DashboardLayoutCard from "../src/components/dashboard-layout-card";

const layouts = [
  {
    layout_id: "main",
    name: "Main Dashboard",
    is_default: true,
    widgets: [
      {
        widget_id: "w1",
        widget_type: "chart",
        title: "Revenue",
        col: 0,
        row: 0,
        width: 2,
        height: 1,
      },
      {
        widget_id: "w2",
        widget_type: "metric",
        title: "Users",
        col: 2,
        row: 0,
        width: 1,
        height: 1,
      },
    ],
  },
  {
    layout_id: "compact",
    name: "Compact View",
    is_default: false,
    widgets: [
      {
        widget_id: "w3",
        widget_type: "table",
        title: "Events",
        col: 0,
        row: 0,
        width: 1,
        height: 1,
      },
      {
        widget_id: "w4",
        widget_type: "chart",
        title: "Traffic",
        col: 1,
        row: 0,
        width: 1,
        height: 1,
      },
      {
        widget_id: "w5",
        widget_type: "metric",
        title: "Errors",
        col: 2,
        row: 0,
        width: 1,
        height: 1,
      },
      { widget_id: "w6", widget_type: "log", title: "Logs", col: 0, row: 1, width: 1, height: 1 },
      {
        widget_id: "w7",
        widget_type: "alert",
        title: "Alerts",
        col: 1,
        row: 1,
        width: 1,
        height: 1,
      },
    ],
  },
];

describe("DashboardLayoutCard", () => {
  it("renders header and count", () => {
    const { container } = render(<DashboardLayoutCard layouts={layouts} appName="My App" />);
    expect(container.textContent).toContain("Dashboard Layouts");
    expect(container.textContent).toContain("2 layouts");
  });

  it("shows layout names", () => {
    const { container } = render(<DashboardLayoutCard layouts={layouts} appName="App" />);
    expect(container.textContent).toContain("Main Dashboard");
    expect(container.textContent).toContain("Compact View");
  });

  it("shows default badge", () => {
    const { container } = render(<DashboardLayoutCard layouts={layouts} appName="App" />);
    expect(container.textContent).toContain("Default");
  });

  it("shows widget count", () => {
    const { container } = render(<DashboardLayoutCard layouts={layouts} appName="App" />);
    expect(container.textContent).toContain("2 widgets");
    expect(container.textContent).toContain("5 widgets");
  });

  it("truncates widget list with +N more", () => {
    const { container } = render(<DashboardLayoutCard layouts={layouts} appName="App" />);
    expect(container.textContent).toContain("+1 more");
  });

  it("shows empty state", () => {
    const { container } = render(<DashboardLayoutCard layouts={[]} appName="App" />);
    expect(container.textContent).toContain("No layouts configured");
  });
});
