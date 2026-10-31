import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiWebhookSubscriptionManagerCard from "../src/components/api-developer-api-api-developer-api-api-webhook-subscription-manager-card";

const subs = [
  { subscription_id: "s1", topic: "order.created", callback_url: "https://billing.example.com/hook", active: true, deliveries: 500, success_rate: 99.5 },
];

describe("Card", () => {
  it("shows subscriptions", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiWebhookSubscriptionManagerCard subscriptions={subs} failingCount={0} appName="App" />);
    expect(container.textContent).toContain("Subscriptions");
    expect(container.textContent).toContain("1 active");
    expect(container.textContent).toContain("order.created");
    expect(container.textContent).toContain("99.5%");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiWebhookSubscriptionManagerCard subscriptions={[]} failingCount={0} appName="App" />);
    expect(container.textContent).toContain("No subscriptions");
  });
});
