import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-usage-alert-card";

describe("UsageAlertCard", () => {
  it("shows alerts", () => {
    const alerts = [{ alert_id: "a1", metric: "error_rate", current_value: 10, threshold: 5, severity: "critical", status: "active" }];
    const { container } = render(<Card alerts={alerts} activeCount={1} appName="App" />);
    expect(container.textContent).toContain("Usage Alerts");
    expect(container.textContent).toContain("1 active");
    expect(container.textContent).toContain("error_rate");
    expect(container.textContent).toContain("10 / 5");
  });
  it("shows no alerts", () => {
    const { container } = render(<Card alerts={[]} activeCount={0} appName="App" />);
    expect(container.textContent).toContain("No alerts");
  });
});
