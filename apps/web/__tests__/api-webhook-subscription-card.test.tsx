import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIWebhookSubscriptionCard from "../src/components/api-webhook-subscription-card";

const subs = [
  { subscription_id: "s1", url: "https://hooks.example.com", event_pattern: "push", enabled: true, delivery_count: 100 },
  { subscription_id: "s2", url: "https://other.com", event_pattern: "issue.*", enabled: false, delivery_count: 5 },
];

describe("APIWebhookSubscriptionCard", () => {
  it("renders header and active count", () => {
    const { container } = render(<APIWebhookSubscriptionCard subscriptions={subs} appName="App" />);
    expect(container.textContent).toContain("Webhook Subscriptions");
    expect(container.textContent).toContain("1/2 active");
  });

  it("shows patterns and delivery counts", () => {
    const { container } = render(<APIWebhookSubscriptionCard subscriptions={subs} appName="App" />);
    expect(container.textContent).toContain("push");
    expect(container.textContent).toContain("issue.*");
    expect(container.textContent).toContain("100 sent");
  });

  it("shows empty state", () => {
    const { container } = render(<APIWebhookSubscriptionCard subscriptions={[]} appName="App" />);
    expect(container.textContent).toContain("No subscriptions");
  });
});
