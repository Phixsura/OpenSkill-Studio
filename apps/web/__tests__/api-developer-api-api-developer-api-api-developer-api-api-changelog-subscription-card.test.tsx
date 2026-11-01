import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiChangelogSubscriptionCard from "../src/components/api-developer-api-api-developer-api-api-developer-api-api-changelog-subscription-card";

const subs = [{ subscription_id: "s1", developer_id: "alice", channels: ["email", "slack"], filters: ["breaking"], notifications_sent: 15, active: true }];

describe("Card", () => {
  it("shows subscriptions", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiChangelogSubscriptionCard subscriptions={subs} activeCount={5} appName="App" />);
    expect(container.textContent).toContain("Changelog Subscriptions");
    expect(container.textContent).toContain("5 active");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("email");
    expect(container.textContent).toContain("15 sent");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiChangelogSubscriptionCard subscriptions={[]} activeCount={0} appName="App" />);
    expect(container.textContent).toContain("No subscriptions");
  });
});
