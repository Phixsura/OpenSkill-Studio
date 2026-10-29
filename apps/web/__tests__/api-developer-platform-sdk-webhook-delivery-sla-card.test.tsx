import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKWebhookDeliverySLACard from "../src/components/api-developer-platform-sdk-webhook-delivery-sla-card";

const slas = [
  { destination: "https://api.example.com", target_delivery_ms: 500, actual_avg_ms: 200, target_success_rate_pct: 99, actual_success_rate_pct: 99.5, meeting_all_sla: true, sla_breaches: 0 },
  { destination: "https://slow.example.com", target_delivery_ms: 200, actual_avg_ms: 800, target_success_rate_pct: 99, actual_success_rate_pct: 95, meeting_all_sla: false, sla_breaches: 3 },
];

describe("Card", () => {
  it("shows SLAs", () => {
    const { container } = render(<APIDeveloperPlatformSDKWebhookDeliverySLACard slas={slas} breachingCount={1} appName="App" />);
    expect(container.textContent).toContain("Delivery SLA");
    expect(container.textContent).toContain("1 breaching");
    expect(container.textContent).toContain("200ms / 500ms");
    expect(container.textContent).toContain("800ms / 200ms");
  });
  it("shows all met", () => {
    const { container } = render(<APIDeveloperPlatformSDKWebhookDeliverySLACard slas={[]} breachingCount={0} appName="App" />);
    expect(container.textContent).toContain("all met");
  });
});
