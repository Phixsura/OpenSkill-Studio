import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIWebhookDigestSubscriptionCard from "../src/components/api-webhook-digest-subscription-card";

const subs = [{ subscription_id: "s1", destination: "https://a.com", frequency: "daily", enabled: true, digest_count: 30 }];

describe("APIWebhookDigestSubscriptionCard", () => {
  it("shows subs", () => {
    const { container } = render(<APIWebhookDigestSubscriptionCard subscriptions={subs} appName="App" />);
    expect(container.textContent).toContain("Digest Subscriptions");
    expect(container.textContent).toContain("daily");
    expect(container.textContent).toContain("30 sent");
  });
  it("shows empty", () => {
    const { container } = render(<APIWebhookDigestSubscriptionCard subscriptions={[]} appName="App" />);
    expect(container.textContent).toContain("No digest subscriptions");
  });
});
