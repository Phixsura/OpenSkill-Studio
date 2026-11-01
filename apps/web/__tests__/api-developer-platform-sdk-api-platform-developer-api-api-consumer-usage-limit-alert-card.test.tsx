import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-usage-limit-alert-card";

describe("UsageLimitAlertCard", () => {
  it("shows alerts", () => {
    const alerts = [{ alert_id: "a1", consumer_id: "c1", metric: "requests", usage_pct: 85, threshold_pct: 75, acknowledged: false }];
    const { container } = render(<Card alerts={alerts} unacknowledgedCount={1} appName="App" />);
    expect(container.textContent).toContain("Usage Alerts");
    expect(container.textContent).toContain("1 unacked");
    expect(container.textContent).toContain("c1 / requests");
    expect(container.textContent).toContain("85%");
  });
  it("shows empty", () => {
    const { container } = render(<Card alerts={[]} unacknowledgedCount={0} appName="App" />);
    expect(container.textContent).toContain("No usage alerts");
  });
});
