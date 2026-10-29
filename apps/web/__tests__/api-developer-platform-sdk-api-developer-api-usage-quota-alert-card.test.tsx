import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperApiUsageQuotaAlertCard from "../src/components/api-developer-platform-sdk-api-developer-api-usage-quota-alert-card";

const alerts = [
  { alert_id: "a1", consumer_id: "acme", resource: "api_calls", threshold_pct: 80, current_usage_pct: 90, triggered: true },
  { alert_id: "a2", consumer_id: "beta", resource: "storage", threshold_pct: 90, current_usage_pct: 50, triggered: false },
];

describe("Card", () => {
  it("shows quota alerts", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiUsageQuotaAlertCard alerts={alerts} triggeredCount={1} appName="App" />);
    expect(container.textContent).toContain("Quota Alerts");
    expect(container.textContent).toContain("1 firing");
    expect(container.textContent).toContain("acme");
    expect(container.textContent).toContain("90% / 80%");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiUsageQuotaAlertCard alerts={[]} triggeredCount={0} appName="App" />);
    expect(container.textContent).toContain("No quota alerts");
  });
});
