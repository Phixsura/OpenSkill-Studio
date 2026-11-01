import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-dashboard-widget-card";

describe("ConsumerApiDashboardWidgetCard", () => {
  it("shows widgets", () => {
    const widgets = [{ id: "w1", type: "metric", title: "API Calls", width: 2, visible: true }, { id: "w2", type: "chart", title: "Latency", width: 1, visible: true }];
    const { container } = render(<Card widgets={widgets} consumerId="c1" layout="grid" appName="App" />);
    expect(container.textContent).toContain("Dashboard Widgets");
    expect(container.textContent).toContain("API Calls");
    expect(container.textContent).toContain("2col");
    expect(container.textContent).toContain("grid layout");
  });
  it("shows empty", () => {
    const { container } = render(<Card widgets={[]} consumerId="c1" layout="list" appName="App" />);
    expect(container.textContent).toContain("No widgets");
  });
});
