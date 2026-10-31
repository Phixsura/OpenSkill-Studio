import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiUsageAlertCard from "../src/components/api-developer-api-api-developer-api-api-usage-alert-card";

const alerts = [
  { alert_id: "a1", metric: "error_rate", threshold: 5, operator: "gt", current_value: 10, triggered: true },
  { alert_id: "a2", metric: "latency_p99", threshold: 1000, operator: "gt", current_value: 500, triggered: false },
];

describe("APIDeveloperAPIApiDeveloperApiApiUsageAlertCard", () => {
  it("shows alerts", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiUsageAlertCard alerts={alerts} triggeredCount={1} appName="App" />);
    expect(container.textContent).toContain("Usage Alerts");
    expect(container.textContent).toContain("1 firing");
    expect(container.textContent).toContain("error_rate");
    expect(container.textContent).toContain("10 > 5");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiUsageAlertCard alerts={[]} triggeredCount={0} appName="App" />);
    expect(container.textContent).toContain("No alerts configured");
  });
});
