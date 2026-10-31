import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-usage-quota-alert-card";

describe("ConsumerApiUsageQuotaAlertCard", () => {
  it("shows alerts and rules", () => {
    const alerts = [{ id: "a1", metric: "requests", usagePct: 92, currentUsage: 920, limit: 1000, triggeredAt: "12:00" }];
    const rules = [{ id: "r1", metric: "requests", thresholdPct: 80, enabled: true }];
    const { container } = render(<Card alerts={alerts} rules={rules} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Quota Alerts");
    expect(container.textContent).toContain("requests at 92%");
    expect(container.textContent).toContain("≥ 80%");
    expect(container.textContent).toContain("ON");
  });
  it("shows empty", () => {
    const { container } = render(<Card alerts={[]} rules={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No quota alert rules");
  });
});
