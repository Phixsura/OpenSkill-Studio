import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiPlatformConsumerWebhookQuotaCard from "../src/components/api-developer-platform-sdk-api-platform-consumer-webhook-quota-card";

const quotas = [
  { consumer_id: "acme", daily_limit: 10000, used_today: 8000, remaining: 2000, usage_pct: 80, exhausted: false },
  { consumer_id: "beta", daily_limit: 1000, used_today: 1000, remaining: 0, usage_pct: 100, exhausted: true },
];

describe("Card", () => {
  it("shows quotas", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformConsumerWebhookQuotaCard quotas={quotas} exhaustedCount={1} appName="App" />);
    expect(container.textContent).toContain("Webhook Quotas");
    expect(container.textContent).toContain("1 exhausted");
    expect(container.textContent).toContain("8,000/10,000");
    expect(container.textContent).toContain("1,000/1,000");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformConsumerWebhookQuotaCard quotas={[]} exhaustedCount={0} appName="App" />);
    expect(container.textContent).toContain("No webhook quotas");
  });
});
