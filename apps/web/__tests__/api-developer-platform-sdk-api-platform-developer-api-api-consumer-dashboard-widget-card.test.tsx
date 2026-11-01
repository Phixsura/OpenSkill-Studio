import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-dashboard-widget-card";

describe("DashboardWidgetCard", () => {
  it("shows widgets", () => {
    const widgets = [{ widget_id: "w1", widget_type: "chart", title: "Requests", data_source: "requests", width: 2 }];
    const { container } = render(<Card dashboardTitle="API Dashboard" widgets={widgets} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("API Dashboard");
    expect(container.textContent).toContain("Requests");
    expect(container.textContent).toContain("requests");
  });
  it("shows empty", () => {
    const { container } = render(<Card dashboardTitle="Dashboard" widgets={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No widgets configured");
  });
});
