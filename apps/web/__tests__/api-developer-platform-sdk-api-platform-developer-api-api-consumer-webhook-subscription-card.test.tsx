import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-webhook-subscription-card";

describe("WebhookSubscriptionCard", () => {
  it("shows subscriptions", () => {
    const subs = [{ subscription_id: "s1", consumer_id: "c1", url: "https://h.com/wh", events: ["order.created", "user.updated"], active: true }];
    const { container } = render(<Card subscriptions={subs} activeCount={1} appName="App" />);
    expect(container.textContent).toContain("Subscriptions");
    expect(container.textContent).toContain("1 active");
    expect(container.textContent).toContain("order.created");
  });
  it("shows empty", () => {
    const { container } = render(<Card subscriptions={[]} activeCount={0} appName="App" />);
    expect(container.textContent).toContain("No subscriptions");
  });
});
